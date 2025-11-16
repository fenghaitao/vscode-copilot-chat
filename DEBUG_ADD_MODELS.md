# Debugging "Add Models" → iflow Flow

## What You Need to Do

The code SHOULD work when you click "Add Models" → iflow, but we need to see the logs to understand why it doesn't.

### Step 1: Reload the Extension
Since we just recompiled:
- If you have Extension Development Host open, press **Cmd+R** or **Ctrl+R** to reload
- Or close it and press **F5** again to launch

### Step 2: Open Logging
**BEFORE** clicking "Add Models":

1. **Open Output Panel**:
   - View → Output
   - Select "GitHub Copilot Chat" from dropdown

2. **Open Developer Tools Console**:
   - Help → Toggle Developer Tools (or Cmd/Ctrl+Shift+I)
   - Go to Console tab

3. **Clear both** so we only see new logs

### Step 3: Click "Add Models" → iflow

In VS Code:
1. Open Copilot Chat (if not open)
2. Click somewhere to access "Language Models" settings
3. Click "Add Models"
4. Click **iflow** in the list

### Step 4: What Logs to Look For

After clicking iflow, you should see logs like:

```
[BYOK iflow] provideLanguageModelChatInformation called with silent=true/false
[BYOK iflow] API key from storage: not found
```

Then ONE of:
- `[BYOK iflow] Silent mode, returning empty list` (if silent=true)
- `[BYOK iflow] Prompting user for API key` (if silent=false) ← **This is what we want!**

### Step 5: Tell Me What You See

Please copy and paste:
1. ALL logs from Output panel that start with `[BYOK` or `[iflow]`
2. ALL logs from Console
3. ANY errors (red text)

Also tell me:
- Did the API key prompt appear? (Yes/No)
- What value is `silent=` in the logs? (true or false)

## Expected Behavior

If `silent=false`:
- ✅ Log: `[BYOK iflow] Prompting user for API key`
- ✅ Log: `[promptForAPIKey] Called for iflow`
- ✅ You should see an input box for API key

If `silent=true`:
- ❌ Log: `[BYOK iflow] Silent mode, returning empty list`  
- ❌ No prompt appears
- **This is the problem** - VS Code is browsing in silent mode

## Theory

I suspect VS Code calls `provideLanguageModelChatInformation` with `silent=true` when showing "Add Models", which means no prompt appears. The prompt only appears when:
- You use the management command (which works - your test command proves it!)
- OR you try to actually USE a model without a key

## Comparison Test

Try this with **Anthropic**:
1. Do you have Anthropic configured already?
2. If YES: Can you see Anthropic models in "Add Models"?
3. If NO: When you click Anthropic in "Add Models", does it prompt for API key?

This will tell us if the "Add Models" flow is supposed to prompt for API keys or not.

## Workaround (That Works!)

Use the test command I created:
1. Command Palette (Cmd/Ctrl+Shift+P)
2. Type: `GitHub Copilot: Configure iflow (Test)`
3. Enter your API key
4. Then iflow models will appear everywhere (including "Add Models")

After entering the key once via the test command, the "Add Models" → iflow should show the models directly.
