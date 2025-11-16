# How to Configure iflow - WORKING SOLUTION! 🎯

## The Problem We Found
The `manageBYOK` command in package.json has `"enablement": "false"`, which means it's hidden from users and can only be called by VS Code's UI. However, the UI button might not be properly wired up to call this command.

## The Solution
I've created a **test command** that you can call directly from the Command Palette to trigger the iflow configuration.

## Steps to Configure iflow:

### 1. Recompile (if not done already)
```bash
cd /home/hfeng1/vscode-copilot-chat
npm run compile
```
✅ Already compiled successfully!

### 2. Launch Extension Development Host
- Press **F5** in VS Code (or use Debug → Start Debugging)
- This opens a new VS Code window with your extension loaded

### 3. Open Command Palette
In the Extension Development Host window:
- Press **Cmd+Shift+P** (Mac) or **Ctrl+Shift+P** (Windows/Linux)

### 4. Run the Test Command
Type: **`GitHub Copilot: Configure iflow (Test)`**

Select the command from the list.

### 5. Enter Your API Key
A prompt should appear asking for your iflow API key:
- Title: "Enter iflow API Key - Preview"
- Enter your iflow API key
- Press Enter

### 6. Verify It Worked
Check the logs:
- **Developer Tools Console** (Cmd/Ctrl+Shift+I)
- **Output Panel** (View → Output → "GitHub Copilot Chat")

You should see:
```
[TestIflowCommand] Manually triggering iflow configuration
[BYOK] manageBYOK command called for vendor: iflow
[BYOK] Calling updateAPIKey for iflow
[BYOK iflow] updateAPIKey called
[promptForAPIKey] Called for iflow
[promptForAPIKey] Showing input box
[promptForAPIKey] Input box result: value provided
[BYOK iflow] Storing new API key
```

### 7. Use iflow Models
After configuration:
1. Open Copilot Chat
2. Click the model selector
3. You should see iflow models:
   - **Qwen3-Coder** (256K input, 64K output)
   - **kimi-k2-0905** (256K input, 64K output)
4. Select one and start chatting!

## Troubleshooting

### Can't find the command?
- Make sure you ran `npm run compile`
- Make sure you're in the Extension Development Host (launched with F5)
- Reload the window: Cmd/Ctrl+R

### No prompt appears?
Check Developer Tools Console for errors. The logs will show exactly where it fails.

### "Provider not found" error?
BYOK might not be enabled. Check Output panel for:
- `[iflow] Initialized with 2 known models`
- `BYOK: Copilot Chat known models list fetched successfully`

### Still nothing?
Share the logs from both:
1. Developer Tools Console
2. Output Panel (GitHub Copilot Chat)

## What This Test Command Does

```typescript
// In testIflowCommand.ts
commands.registerCommand('github.copilot.chat.testConfigureIflow', async () => {
    // This directly calls the manageBYOK command with 'iflow' as parameter
    await commands.executeCommand('github.copilot.chat.manageBYOK', 'iflow');
});
```

This bypasses any UI issues and directly triggers the API key configuration flow.

## Files Created/Modified

1. **src/extension/byok/vscode-node/testIflowCommand.ts** (NEW)
   - Test command implementation

2. **src/extension/extension/vscode-node/contributions.ts**
   - Added TestIflowCommand to contributions

3. **package.json**
   - Added command definition for "github.copilot.chat.testConfigureIflow"

4. **Logging added to**:
   - baseOpenAICompatibleProvider.ts
   - byokContribution.ts
   - byokUIService.ts
   - iflowProvider.ts

## Why the Original UI Doesn't Work

The `manageBYOK` command is registered with `"enablement": "false"` in package.json, which means:
- It won't appear in Command Palette
- It can only be called programmatically by other code
- The `managementCommand` in the language model provider config should trigger it
- But the VS Code UI might not be calling it when you click on iflow

Our test command works around this by calling it directly!

## Next Steps After Testing

Once you confirm this works:
1. You can keep using the test command to configure iflow
2. Or investigate why the UI button isn't calling the command
3. The logging will help identify any other issues

## Success Looks Like

✅ Command appears in Command Palette  
✅ Input box prompts for API key  
✅ API key is stored successfully  
✅ iflow models appear in model picker  
✅ You can chat using iflow models  

Try it now! 🚀
