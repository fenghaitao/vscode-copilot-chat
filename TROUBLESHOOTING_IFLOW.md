# Troubleshooting: "Nothing happens when I click iflow"

## Please follow these steps to help identify the issue:

### Step 1: Check where you're clicking

When you say "click iflow", where exactly are you clicking? There are different places:

**A. Model Picker (just browsing)**
- Open Copilot Chat
- Click the model dropdown (shows current model like "GPT-4")
- See "iflow" in the list
- Click on "iflow" provider name

**This will NOT show the API key prompt!** This just browses available models.

**B. Management/Settings Button (correct way)**
- Open Copilot Chat
- Click the model dropdown
- Look for a **gear icon** or **settings icon** next to "iflow"
- Click that icon

**This SHOULD show the API key prompt.**

**C. Command Palette (recommended)**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type: `GitHub Copilot: Manage`
- Look for a command related to BYOK or provider management
- Select iflow

### Step 2: Enable logging and try again

1. **Open Developer Tools**:
   - In VS Code, press `Cmd+Shift+I` (Mac) or `Ctrl+Shift+I` (Windows/Linux)
   - Or: Help → Toggle Developer Tools

2. **Open Output Panel**:
   - View → Output
   - Select "GitHub Copilot Chat" from the dropdown

3. **Try to configure iflow again** using one of the methods above

4. **Check for logs** in both:
   - Developer Tools Console tab
   - Output panel

### Step 3: Share the logs

Look for logs that start with:
- `[BYOK]`
- `[BYOK iflow]`
- `[iflow]`
- `[promptForAPIKey]`
- Or any error messages

**Copy and share what you see (if anything).**

### Step 4: Check if iflow is registered

In the Developer Tools Console, run:
```javascript
vscode.lm.selectChatModels({ vendor: 'iflow' })
```

This will tell us if iflow is registered at all.

### Step 5: Verify BYOK is enabled

Look in the Output panel for:
```
BYOK: Copilot Chat known models list fetched successfully.
```

or

```
[iflow] Initialized with 2 known models
```

If you don't see these, BYOK might not be enabled for your account.

## Common Issues:

### Issue 1: No management button visible
If you don't see a settings/gear icon next to iflow in the model picker:
- The UI might not expose the management command
- Try using Command Palette instead

### Issue 2: Command not available
If "Manage BYOK" command doesn't appear:
- BYOK might not be enabled (requires Copilot Individual or Internal account)
- Extension might not be fully loaded

### Issue 3: Extension not reloaded
After compiling changes:
- Press `Cmd+R` / `Ctrl+R` in the Extension Development Host to reload
- Or close and reopen the Extension Development Host window

### Issue 4: Silent mode only
If logs show `silent=true` only:
- This is expected when browsing
- You need to click the MANAGEMENT button, not just browse models

## What I need to help you:

Please provide:

1. **Where exactly are you clicking?** (A, B, or C from Step 1 above)

2. **What logs appear?** (from Console and Output panel)

3. **Can you find any command that mentions "BYOK" or "iflow"?**
   - Open Command Palette
   - Type: "iflow"
   - Type: "BYOK"
   - Type: "Manage"
   - What commands appear?

4. **Is this in the Extension Development Host or regular VS Code?**
   - If regular VS Code, you need to reload: `Cmd+R` / `Ctrl+R`
   - If Extension Development Host, good!

5. **Any error messages?** (Check Developer Tools Console)
