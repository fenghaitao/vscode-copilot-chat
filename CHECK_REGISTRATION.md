# Check if iflow is Registered

## If you see NO logs when clicking iflow, the provider might not be registered.

### Step 1: Check Startup Logs

1. **Reload the extension**: Cmd/Ctrl+R (or F5)
2. **Immediately check Output panel**: View → Output → "GitHub Copilot Chat"
3. **Look for these logs at startup**:
   ```
   BYOK: Copilot Chat known models list fetched successfully.
   [iflow] Initialized with 2 known models
   ```

If you **don't see** these logs, iflow is not being registered.

### Step 2: Check if BYOK is Enabled

Look for this log at startup:
```
BYOK: Copilot Chat known models list fetched successfully
```

If you don't see it, BYOK might not be enabled for your account.

**BYOK Requirements**:
- Copilot Individual subscription OR
- Copilot Internal (Microsoft employee) account
- NOT on GitHub Enterprise Server

### Step 3: Search for "iflow" in Logs

In the Output panel, search for "iflow" (Cmd/Ctrl+F).

What do you see?
- Nothing at all? → Provider not registered
- Initialization message? → Provider registered but not called

### Step 4: Check Available Language Model Providers

In Developer Tools Console, run:
```javascript
vscode.lm.onDidChangeChatModels
```

Then click "Add Models" and see if any event fires.

### Step 5: Check Registration Code

The registration happens in `byokContribution.ts` line 95:
```typescript
this._providers.set(IflowBYOKLMProvider.providerName.toLowerCase(), 
    instantiationService.createInstance(IflowBYOKLMProvider, ...));
```

This should run when BYOK is enabled and you're authenticated.

## Questions for You:

1. **Do you see the startup logs** (`[iflow] Initialized with 2 known models`)?
2. **Do you see** `BYOK: Copilot Chat known models list fetched successfully`?
3. **What Copilot account type** do you have? (Individual/Business/Enterprise)
4. **Can you see OTHER BYOK providers** in "Add Models"? (Anthropic, Groq, OpenAI, etc.)
5. **Did you use F5** to launch Extension Development Host, or are you testing in regular VS Code?

## Most Likely Issue

If you're testing in **regular VS Code** (not Extension Development Host):
- Your changes haven't been loaded
- **Solution**: Press F5 to launch Extension Development Host with your changes

## Alternative: Force Registration Check

Add this to check if provider is registered:

1. Open Command Palette
2. Run: `Developer: Show Running Extensions`
3. Find "GitHub.copilot-chat"
4. Check if it's running

Then in Console:
```javascript
// Check if lm API exists
console.log(vscode.lm);
```
