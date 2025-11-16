/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
import { CancellationToken, LanguageModelChatInformation } from 'vscode';
import { ILogService } from '../../../platform/log/common/logService';
import { IFetcherService } from '../../../platform/networking/common/fetcherService';
import { IInstantiationService } from '../../../util/vs/platform/instantiation/common/instantiation';
import { BYOKAuthType, BYOKKnownModels, byokKnownModelsToAPIInfo } from '../common/byokProvider';
import { BaseOpenAICompatibleLMProvider } from './baseOpenAICompatibleProvider';
import { IBYOKStorageService } from './byokStorageService';

// Default models for iflow if not provided by CDN
const defaultIflowModels: BYOKKnownModels = {
	'Qwen3-Coder': {
		name: 'Qwen3-Coder',
		maxInputTokens: 256000,
		maxOutputTokens: 64000,
		toolCalling: true,
		vision: true
	},
	'kimi-k2-0905': {
		name: 'kimi-k2-0905',
		maxInputTokens: 256000,
		maxOutputTokens: 64000,
		toolCalling: true,
		vision: true
	}
};

export class IflowBYOKLMProvider extends BaseOpenAICompatibleLMProvider {
	public static readonly providerName = 'iflow';
	private readonly _mergedModels: BYOKKnownModels;

	constructor(
		knownModels: BYOKKnownModels,
		byokStorageService: IBYOKStorageService,
		@IFetcherService _fetcherService: IFetcherService,
		@ILogService _logService: ILogService,
		@IInstantiationService _instantiationService: IInstantiationService,
	) {
		// Merge CDN models with default models, with CDN taking precedence
		// Handle case where knownModels is undefined (not in CDN)
		const mergedModels = { ...defaultIflowModels, ...(knownModels || {}) };

		// Call super() FIRST before accessing 'this'
		super(
			BYOKAuthType.GlobalApiKey,
			IflowBYOKLMProvider.providerName,
			'https://apis.iflow.cn/v1',
			mergedModels,
			byokStorageService,
			_fetcherService,
			_logService,
			_instantiationService,
		);

		// Now we can access 'this' and use the logger
		this._mergedModels = mergedModels;
		this._logService.info(`[iflow] Initialized with ${Object.keys(mergedModels).length} known models`);
	}

	// Override to ensure iflow appears in "Add Models" even without API key configured
	async provideLanguageModelChatInformation(options: { silent: boolean }, token: CancellationToken): Promise<LanguageModelChatInformation[]> {
		this._logService.info(`[iflow] provideLanguageModelChatInformation called with silent=${options.silent}`);

		// Check if we have an API key
		const apiKey = await this._byokStorageService.getAPIKey(IflowBYOKLMProvider.providerName);
		this._logService.info(`[iflow] API key status: ${apiKey ? 'configured' : 'not configured'}`);

		if (apiKey) {
			// If we have API key, use parent class behavior to fetch from API
			this._logService.info(`[iflow] Delegating to parent class`);
			return super.provideLanguageModelChatInformation(options, token);
		}

		// No API key configured:
		// - In silent mode: still return default models so iflow appears in "Add Models"
		// - In non-silent mode: prompt for API key first
		if (options.silent) {
			this._logService.info(`[iflow] Silent mode without API key - returning default models for visibility`);
			return byokKnownModelsToAPIInfo(IflowBYOKLMProvider.providerName, this._mergedModels);
		} else {
			// Non-silent: prompt for API key, then return models if successful
			this._logService.info(`[iflow] Non-silent mode without API key - will prompt user`);
			return super.provideLanguageModelChatInformation(options, token);
		}
	}

	// Override getAllModels to return default models when API call fails
	// iflow API might not have a /models endpoint, or it might return 404
	protected override async getAllModels(): Promise<BYOKKnownModels> {
		try {
			// Try to fetch models from iflow API
			this._logService.info(`[iflow] Attempting to fetch models from API`);
			return await super.getAllModels();
		} catch (error) {
			// If API call fails (404 or other error), use default models
			this._logService.warn(`[iflow] API call failed (${error}), using default models`);
			return this._mergedModels;
		}
	}
}
