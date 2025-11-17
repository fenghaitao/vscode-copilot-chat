# iflow BYOK Setup Guide

This guide explains how to configure and use iflow as a Bring Your Own Key (BYOK) provider in GitHub Copilot.

## Overview

iflow is an OpenAI-compatible API provider that requires weekly API key rotation. This guide will help you set up and maintain your iflow integration.

## Prerequisites

- GitHub Copilot extension installed
- An active iflow account with API access
- A valid iflow API key

## Initial Setup

### Step 1: Get Your iflow API Key

1. Log in to your iflow account at [https://apis.iflow.cn](https://apis.iflow.cn)
2. Navigate to your API settings or dashboard
3. Generate or copy your API key
4. **Important**: Save this key securely as you'll need to update it weekly

### Step 2: Configure iflow in VS Code

1. Open the Command Palette:
   - **Windows/Linux**: `Ctrl+Shift+P`
   - **macOS**: `Cmd+Shift+P`

2. Type and select: `GitHub Copilot: Update iflow API Key`

3. In the input box that appears:
   - Paste your iflow API key
   - Press `Enter` to save

4. Your iflow provider is now configured and ready to use!

## Using iflow Models

Once configured, iflow models will appear in your GitHub Copilot model selector. Available models include:

- **Qwen3-Coder**: Advanced coding model with 256K context window
- **kimi-k2-0905**: General-purpose model with vision support

To use an iflow model:

1. Open GitHub Copilot Chat
2. Click on the model selector
3. Choose an iflow model from the list
4. Start chatting!

## Weekly API Key Update

**Important**: iflow requires you to update your API key every week.

### Quick Update Process

1. Get your new API key from iflow
2. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
3. Type: `GitHub Copilot: Update iflow API Key`
4. Paste your new API key
5. Press `Enter`

**That's it!** The update takes less than 10 seconds.

### Setting a Reminder

To avoid service interruption, we recommend:

- Setting a weekly calendar reminder to update your iflow API key
- Updating the key on the same day each week (e.g., every Monday)
- Keeping your iflow dashboard bookmarked for quick access

## Alternative: Programmatic Update

For automation or CI/CD environments, you can update the API key programmatically:

```bash
# Set your API key as an environment variable
export IFLOW_API_KEY="your-new-api-key-here"

# Update via command
code --command github.copilot.chat.manageBYOKAPIKey iflow IFLOW_API_KEY update
```

## Troubleshooting

### API Key Not Working

If you receive authentication errors:

1. Verify your API key is correct and not expired
2. Check if it's been more than 7 days since your last update
3. Get a fresh API key from iflow and update it

### Models Not Appearing

If iflow models don't appear in the model selector:

1. Ensure you've entered a valid API key
2. Restart VS Code
3. Check the Output panel (View → Output → GitHub Copilot) for errors

### Removing iflow Configuration

To remove your iflow API key:

1. Open Command Palette
2. Type: `GitHub Copilot: Update iflow API Key`
3. Leave the input box empty
4. Press `Enter`

This will delete your stored API key.

## Security Notes

- Your API key is stored securely using VS Code's built-in secrets storage
- The key is encrypted and never exposed in plain text
- Each workspace can have its own API key configuration
- API keys are never logged or transmitted except to the iflow API endpoint

## Support

For issues related to:
- **iflow API or account**: Contact iflow support
- **GitHub Copilot integration**: Check the [main documentation](../README.md) or file an issue

## Additional Resources

- [iflow Documentation](https://apis.iflow.cn/docs)
- [GitHub Copilot BYOK Overview](./byok-overview.md)
- [Troubleshooting Guide](../TROUBLESHOOTING_IFLOW.md)
