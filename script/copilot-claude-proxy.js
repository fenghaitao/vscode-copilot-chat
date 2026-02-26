#!/usr/bin/env node
/**
 * Standalone Copilot → Anthropic Messages API Proxy
 *
 * Starts a local HTTP server that accepts Anthropic Messages API requests
 * and forwards them to the GitHub Copilot API (CAPI), so you can run the
 * Claude Code CLI (or any Anthropic SDK client) using your GitHub Copilot
 * subscription — no separate Anthropic API key required.
 *
 * How it works:
 *   1. Exchanges your GitHub token for a short-lived Copilot token
 *      (same flow as the VS Code extension does internally)
 *   2. Starts an HTTP server on a fixed port that speaks the Anthropic
 *      Messages API format
 *   3. Forwards incoming requests to CAPI's /v1/messages endpoint,
 *      substituting Copilot token auth and mapping model names
 *   4. Streams the response back to the caller
 *
 * Usage:
 *   GITHUB_TOKEN=ghp_xxxx node script/copilot-claude-proxy.js
 *
 * Then in another terminal:
 *   ANTHROPIC_BASE_URL=http://127.0.0.1:4141 ANTHROPIC_AUTH_TOKEN=any-value claude
 *
 * Optional environment variables:
 *   PORT          Port to listen on (default: 4141)
 *   SECRET        Optional shared secret for Authorization/x-api-key validation.
 *                 If set, incoming requests must include this value.
 *                 If unset, all requests are accepted (safe for localhost use).
 *   VERBOSE       Set to '1' to log SSE chunks to stdout
 *   GITHUB_TOKEN  Required. GitHub personal access token with Copilot access.
 *
 * Requirements:
 *   - Node.js 18+ (uses built-in https module, no npm dependencies)
 *   - A GitHub account with an active Copilot subscription
 *   - Claude Code CLI installed: https://code.claude.com
 */

'use strict';

const http = require('http');
const https = require('https');

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const PORT = parseInt(process.env.PORT ?? '4141', 10);
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const SECRET = process.env.SECRET;       // optional auth gate
const VERBOSE = process.env.VERBOSE === '1';
const DEFAULT_CAPI_BASE = 'https://api.githubcopilot.com';

/**
 * Anthropic beta features that CAPI supports.
 * Matches the SUPPORTED_ANTHROPIC_BETAS list in claudeLanguageModelServer.ts.
 */
const SUPPORTED_BETAS = [
	'interleaved-thinking',
	'context-management',
	'advanced-tool-use',
];

if (!GITHUB_TOKEN) {
	console.error('Error: GITHUB_TOKEN environment variable is required.\n');
	console.error('Set it to a GitHub personal access token with Copilot access.');
	console.error('You can create one at: https://github.com/settings/tokens');
	process.exit(1);
}

// ---------------------------------------------------------------------------
// Copilot token management
// ---------------------------------------------------------------------------

let cachedToken = null;
let tokenExpiresAt = 0;
let capiBaseUrl = DEFAULT_CAPI_BASE;

function httpsGet(urlOrOptions) {
	return new Promise((resolve, reject) => {
		const req = https.request(urlOrOptions, (res) => {
			let body = '';
			res.on('data', chunk => body += chunk);
			res.on('end', () => resolve({ status: res.statusCode, body }));
		});
		req.on('error', reject);
		req.end();
	});
}

/**
 * Fetches a short-lived Copilot token from GitHub.
 * Mirrors the logic in copilotTokenManager.ts: fetchCopilotTokenFromGitHubToken()
 */
async function fetchCopilotToken() {
	const result = await httpsGet({
		hostname: 'api.github.com',
		path: '/copilot_internal/v2/token',
		method: 'GET',
		headers: {
			Authorization: `token ${GITHUB_TOKEN}`,
			'User-Agent': 'GitHubCopilotChat/standalone-proxy',
			// These headers are required by the Copilot token endpoint
			// (mirrors getEditorVersionHeaders() in envService.ts)
			'Editor-Version': 'vscode/1.100.0',
			'Editor-Plugin-Version': 'copilot-chat/0.26.0',
			// NOTE: Do NOT include X-GitHub-Api-Version here — that header routes
			// the request through the versioned REST API which does not expose
			// the copilot_internal endpoint, resulting in a 404.
		},
	});

	if (result.status !== 200) {
		let hint = '';
		if (result.status === 401) {
			hint = 'Token is invalid or expired. Regenerate at https://github.com/settings/tokens';
		} else if (result.status === 403) {
			hint = 'Access denied. Does your account have an active GitHub Copilot subscription?';
		} else if (result.status === 404) {
			hint = 'Endpoint not found. This can happen if:\n' +
				'  - Your GITHUB_TOKEN is a fine-grained PAT (use a classic PAT instead)\n' +
				'  - Your token does not have the required scopes (needs read:user at minimum)\n' +
				'  - Your account does not have an active Copilot subscription';
		}
		throw new Error(
			`Copilot token fetch failed: HTTP ${result.status}. ${hint}\nResponse: ${result.body}`
		);
	}

	let envelope;
	try {
		envelope = JSON.parse(result.body);
	} catch (e) {
		throw new Error(`Failed to parse token response: ${e.message}`);
	}

	if (!envelope.token || !envelope.expires_at) {
		throw new Error(`Unexpected token response shape: ${JSON.stringify(envelope)}`);
	}

	return envelope;
}

/**
 * Returns a valid Copilot token, refreshing if it will expire soon.
 */
async function getCopilotToken() {
	const nowSeconds = Math.floor(Date.now() / 1000);
	// Refresh when token has less than 60 seconds left (matches extension logic)
	if (cachedToken && tokenExpiresAt > nowSeconds + 60) {
		return cachedToken;
	}

	console.log('[proxy] Fetching fresh Copilot token...');
	const envelope = await fetchCopilotToken();

	cachedToken = envelope.token;
	// Use expires_at directly; add a small buffer as the extension does
	tokenExpiresAt = envelope.expires_at;

	// Use the SKU-specific endpoint if the server returned one (see Endpoints interface)
	if (envelope.endpoints?.api) {
		capiBaseUrl = envelope.endpoints.api.replace(/\/$/, '');
	}

	console.log(
		`[proxy] Token acquired. Expires: ${new Date(tokenExpiresAt * 1000).toISOString()} | ` +
		`CAPI: ${capiBaseUrl} | SKU: ${envelope.sku ?? 'unknown'}`
	);

	return cachedToken;
}

// ---------------------------------------------------------------------------
// Model name mapping
// ---------------------------------------------------------------------------

/**
 * Static model overrides: maps any incoming model ID to a fixed CAPI model.
 * All entries point to github_copilot/gpt-4o.
 */
const MODEL_MAP = {
	'claude-opus-4-6': 'github_copilot/gpt-4o',
	'claude-sonnet-4-6': 'github_copilot/gpt-4o',
	'claude-opus-4-5': 'github_copilot/gpt-4o',
	'claude-sonnet-4-5': 'github_copilot/gpt-4o',
	'claude-haiku-4-5': 'github_copilot/gpt-4o',
	'claude-opus-4': 'github_copilot/gpt-4o',
	'claude-sonnet-4': 'github_copilot/gpt-4o',
	'claude-haiku-4': 'github_copilot/gpt-4o',
	'claude-3-5-sonnet-20241022': 'github_copilot/gpt-4o',
	'claude-3-5-haiku-20241022': 'github_copilot/gpt-4o',
	'claude-3-opus-20240229': 'github_copilot/gpt-4o',
	'claude-3-sonnet-20240229': 'github_copilot/gpt-4o',
	'claude-3-haiku-20240307': 'github_copilot/gpt-4o',
};

/**
 * Maps Anthropic SDK model IDs to the format CAPI expects.
 * First checks MODEL_MAP for a static override, then applies dynamic
 * date-suffix transformation for any remaining claude- models.
 * e.g. claude-sonnet-4-20250514   → claude-sonnet-4.20250514
 *      claude-sonnet-4-5-20250929 → claude-sonnet-4.5
 *      claude-haiku-4-5-20251001  → claude-haiku-4.5
 * Mirrors selectEndpoint() logic in claudeLanguageModelServer.ts
 */
function mapModelName(model) {
	if (!model) {
		return model;
	}
	// Normalize: strip trailing 8-digit date suffix so map keys like
	// 'claude-haiku-4-5' match incoming IDs like 'claude-haiku-4-5-20251001'.
	let normalized = model;
	if (model.startsWith('claude-')) {
		const parts = model.split('-');
		if (parts.length >= 4 && /^\d{8}$/.test(parts[parts.length - 1])) {
			normalized = parts.slice(0, -1).join('-');
		}
	}
	// Check static override map with normalized ID
	if (MODEL_MAP[normalized]) {
		return MODEL_MAP[normalized];
	}
	// Check static override map with original ID (handles versioned IDs like
	// 'claude-3-5-sonnet-20241022' that are in the map verbatim)
	if (MODEL_MAP[model]) {
		return MODEL_MAP[model];
	}
	if (!model.startsWith('claude-')) {
		return model;
	}
	// Dynamic date-suffix transformation for unlisted models
	const parts = model.split('-');
	if (parts.length >= 4 && /^\d{8}$/.test(parts[parts.length - 1])) {
		const date = parts.pop();
		// If the new last segment is also numeric (sub-version e.g. "5" in "4-5"),
		// this is a x.y model like claude-sonnet-4.5. CAPI expects no date suffix for these.
		// e.g. claude-sonnet-4-5-20250929 → claude-sonnet-4.5
		if (/^\d+$/.test(parts[parts.length - 1])) {
			const minor = parts.pop();
			return `${parts.join('-')}.${minor}`;
		}
		// For single-version models, keep the date with dot notation.
		// e.g. claude-sonnet-4-20250514 → claude-sonnet-4.20250514
		return `${parts.join('-')}.${date}`;
	}
	return model;
}

// ---------------------------------------------------------------------------
// Beta header filtering
// ---------------------------------------------------------------------------

/**
 * Keeps only the anthropic-beta values that CAPI supports.
 * Mirrors filterSupportedBetas() in claudeLanguageModelServer.ts
 */
function filterBetas(headerValue) {
	if (!headerValue) {
		return undefined;
	}
	const filtered = headerValue
		.split(',')
		.map(b => b.trim())
		.filter(b => SUPPORTED_BETAS.some(supported => b.startsWith(supported)));
	return filtered.length > 0 ? filtered.join(', ') : undefined;
}

// ---------------------------------------------------------------------------
// Auth validation
// ---------------------------------------------------------------------------

/**
 * Validates the incoming request's API key/auth header against SECRET.
 * If SECRET is not set, all requests are accepted.
 * Supports both x-api-key and Authorization: Bearer formats (same as the
 * extension's extractSessionId() function).
 */
function isAuthorized(headers) {
	if (!SECRET) {
		return true; // no auth required
	}

	const apiKey = headers['x-api-key'];
	if (typeof apiKey === 'string' && apiKey === SECRET) {
		return true;
	}

	const auth = headers['authorization'];
	if (typeof auth === 'string' && auth.startsWith('Bearer ')) {
		// Accept "SECRET" or "SECRET.<sessionId>" (nonce.sessionId format from CLI)
		const value = auth.slice(7);
		return value === SECRET || value.startsWith(SECRET + '.');
	}

	return false;
}

// ---------------------------------------------------------------------------
// Core proxy logic
// ---------------------------------------------------------------------------

/**
 * Reads a full request body from an IncomingMessage.
 */
function readBody(req) {
	return new Promise((resolve, reject) => {
		let body = '';
		req.on('data', chunk => body += chunk.toString());
		req.on('end', () => resolve(body));
		req.on('error', reject);
	});
}

/**
 * Sends a structured Anthropic-style error response.
 */
function sendError(res, status, type, message) {
	if (res.headersSent) {
		return;
	}
	res.writeHead(status, { 'Content-Type': 'application/json' });
	res.end(JSON.stringify({ type: 'error', error: { type, message } }));
}

/**
 * Proxies one Messages API request through to CAPI.
 */
async function proxyMessagesRequest(reqBody, reqHeaders, res) {
	const copilotToken = await getCopilotToken();

	let bodyObj;
	try {
		bodyObj = JSON.parse(reqBody);
	} catch {
		return sendError(res, 400, 'invalid_request_error', 'Request body must be valid JSON.');
	}

	// Map model name to the format CAPI expects
	const originalModel = bodyObj.model;
	if (bodyObj.model) {
		bodyObj.model = mapModelName(bodyObj.model);
	}

	const bodyString = JSON.stringify(bodyObj);
	const capiUrl = new URL(`${capiBaseUrl}/v1/messages`);

	// Build outgoing headers
	const outHeaders = {
		Authorization: `Bearer ${copilotToken}`,
		'Content-Type': 'application/json',
		'Content-Length': String(Buffer.byteLength(bodyString)),
		'User-Agent': 'GitHubCopilotChat/standalone-proxy',
		// Identifies request origin to CAPI for quota/analytics
		'Copilot-Integration-Id': 'vscode-chat',
		'Editor-Version': 'vscode/1.100.0',
		'Editor-Plugin-Version': 'copilot-chat/standalone',
	};

	// Pass through filtered anthropic-beta
	const beta = filterBetas(reqHeaders['anthropic-beta']);
	if (beta) {
		outHeaders['anthropic-beta'] = beta;
	}

	console.log(
		`[proxy] → POST ${capiUrl.host}/v1/messages | model: ${originalModel} → ${bodyObj.model} | stream: ${!!bodyObj.stream}`
	);

	return new Promise((resolve, reject) => {
		const capiReq = https.request(
			{
				hostname: capiUrl.hostname,
				port: capiUrl.port || 443,
				path: capiUrl.pathname,
				method: 'POST',
				headers: outHeaders,
			},
			(capiRes) => {
				console.log(`[proxy] ← HTTP ${capiRes.statusCode}`);

				// Forward a minimal set of useful response headers
				const responseHeaders = {
					'Content-Type': capiRes.headers['content-type'] ?? 'application/json',
				};
				for (const hdr of ['x-request-id', 'x-github-request-id', 'anthropic-ratelimit-requests-remaining', 'anthropic-ratelimit-tokens-remaining']) {
					if (capiRes.headers[hdr]) {
						responseHeaders[hdr] = capiRes.headers[hdr];
					}
				}

				res.writeHead(capiRes.statusCode, responseHeaders);

				capiRes.on('data', chunk => {
					if (VERBOSE) {
						process.stdout.write(chunk.toString());
					}
					res.write(chunk);
				});
				capiRes.on('end', () => {
					res.end();
					resolve();
				});
				capiRes.on('error', (err) => {
					console.error('[proxy] CAPI response stream error:', err.message);
					sendError(res, 502, 'api_error', `Upstream stream error: ${err.message}`);
					resolve();
				});
			}
		);

		capiReq.on('error', (err) => {
			console.error('[proxy] CAPI connection error:', err.message);
			sendError(res, 502, 'api_error', `Could not connect to CAPI: ${err.message}`);
			resolve();
		});

		capiReq.write(bodyString);
		capiReq.end();
	});
}

// ---------------------------------------------------------------------------
// HTTP server
// ---------------------------------------------------------------------------

const server = http.createServer(async (req, res) => {
	// CORS preflight (needed if calling from a browser-based client)
	if (req.method === 'OPTIONS') {
		res.writeHead(200, {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Headers': 'content-type, x-api-key, authorization, anthropic-beta, anthropic-version',
			'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
		});
		res.end();
		return;
	}

	const pathname = new URL(req.url ?? '/', 'http://localhost').pathname;

	// Health check
	if (req.method === 'GET' && pathname === '/') {
		res.writeHead(200, { 'Content-Type': 'text/plain' });
		res.end(
			`Copilot Claude Proxy\n` +
			`CAPI base: ${capiBaseUrl}\n` +
			`Token expires: ${new Date(tokenExpiresAt * 1000).toISOString()}\n`
		);
		return;
	}

	// Messages API endpoint — matches all the path variants that the extension handles
	if (
		req.method === 'POST' &&
		(pathname === '/v1/messages' || pathname === '/messages' || pathname === '//messages')
	) {
		if (!isAuthorized(req.headers)) {
			return sendError(res, 401, 'authentication_error', 'Unauthorized. Set ANTHROPIC_AUTH_TOKEN (or x-api-key) to the SECRET value.');
		}

		try {
			const body = await readBody(req);
			await proxyMessagesRequest(body, req.headers, res);
		} catch (err) {
			console.error('[proxy] Unhandled error:', err.message);
			sendError(res, 500, 'api_error', err.message);
		}
		return;
	}

	sendError(res, 404, 'not_found_error', `No route: ${req.method} ${pathname}`);
});

// ---------------------------------------------------------------------------
// Startup
// ---------------------------------------------------------------------------

console.log('Copilot Claude Proxy — starting...\n');

getCopilotToken()
	.then(() => {
		server.listen(PORT, '127.0.0.1', () => {
			console.log(`\n✓ Proxy listening on http://127.0.0.1:${PORT}`);
			console.log('\n── Claude Code CLI ──────────────────────────────────────────');
			console.log(`  ANTHROPIC_BASE_URL=http://127.0.0.1:${PORT} ANTHROPIC_AUTH_TOKEN=any-value claude`);
			console.log('\n── Claude Agent SDK (Node) ──────────────────────────────────');
			console.log(`  ANTHROPIC_BASE_URL=http://127.0.0.1:${PORT} ANTHROPIC_API_KEY=any-value node your-script.js`);
			if (SECRET) {
				console.log(`\n── Auth: SECRET is set. Use it as ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY. ──`);
			} else {
				console.log('\n── Auth: No SECRET set. All local requests accepted. ────────');
			}
			console.log('─────────────────────────────────────────────────────────────\n');
		});
	})
	.catch(err => {
		console.error('\n✗ Failed to start proxy:', err.message);
		process.exit(1);
	});
