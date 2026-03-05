# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [package.json](file://package.json)
- [.github/copilot-instructions.md](file://.github/copilot-instructions.md)
- [src/extension/extension/vscode/extension.ts](file://src/extension/extension/vscode/extension.ts)
- [src/extension/inlineChat/node/inlineChatIntent.ts](file://src/extension/inlineChat/node/inlineChatIntent.ts)
- [src/extension/intents/node/allIntents.ts](file://src/extension/intents/node/allIntents.ts)
- [src/extension/getting-started/vscode-node/gettingStarted.ts](file://src/extension/getting-started/vscode-node/gettingStarted.ts)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Initial Setup](#initial-setup)
5. [Basic Workflow](#basic-workflow)
6. [Modes and How to Enable Them](#modes-and-how-to-enable-them)
7. [Quick Start Examples](#quick-start-examples)
8. [Initial Configuration and Customization](#initial-configuration-and-customization)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Conclusion](#conclusion)

## Introduction
GitHub Copilot Chat brings AI-powered collaboration directly into Visual Studio Code. You can chat with an AI assistant, use inline chat for precise, in-editor edits, leverage autonomous agents for complex tasks, and receive intelligent inline suggestions to accelerate your coding.

## Prerequisites
- Active GitHub Copilot subscription is required to access Copilot Chat features.
- Ensure your VS Code version meets the compatibility requirement enforced by the extension.

Key compatibility indicators:
- The extension enforces a minimum VS Code version in its manifest.
- The extension is released in lockstep with VS Code, meaning newer versions of the extension require the latest VS Code.

**Section sources**
- [README.md](file://README.md#L12-L17)
- [README.md](file://README.md#L55-L60)
- [package.json](file://package.json#L25-L29)

## Installation
Install the extension from the VS Code Marketplace:
- Open VS Code.
- Go to Extensions (Ctrl+Shift+X or Cmd+Shift+X).
- Search for “GitHub Copilot Chat”.
- Click Install.

After installation, reload VS Code if prompted.

**Section sources**
- [README.md](file://README.md#L12-L17)
- [package.json](file://package.json#L1-L10)

## Initial Setup
Upon first launch, the extension initializes its services and contributions. Activation checks include:
- Ensuring compatibility with the current VS Code version.
- Initializing the contribution system and services.
- Preparing chat participants and UI integrations.

Important activation behaviors:
- The extension verifies the VS Code environment and sets context flags to guide users when using pre-release builds on stable channels.
- Services are registered and contributions are loaded to enable chat, inline chat, and agent features.

**Section sources**
- [src/extension/extension/vscode/extension.ts](file://src/extension/extension/vscode/extension.ts#L33-L75)
- [src/extension/extension/vscode/extension.ts](file://src/extension/extension/vscode/extension.ts#L41-L50)

## Basic Workflow
Once installed and activated:
- Access Copilot Chat from the sidebar or command palette.
- Start a new chat session to ask questions, request explanations, or delegate tasks to an agent.
- Use inline chat to propose targeted edits directly in the editor.
- Switch between modes as needed for different workflows.

Common entry points:
- Chat participants and intents are registered to support diverse workflows such as explaining code, fixing issues, generating content, and more.

**Section sources**
- [.github/copilot-instructions.md](file://.github/copilot-instructions.md#L157-L172)
- [src/extension/intents/node/allIntents.ts](file://src/extension/intents/node/allIntents.ts#L32-L52)

## Modes and How to Enable Them
The extension supports several modes integrated into VS Code’s chat and inline editing systems:

- Agent mode
  - Purpose: Autonomous multi-step tasks across files and commands.
  - Availability: Provided as a chat participant and integrated with VS Code’s chat UI.
  - Enabling: Available after installing the extension and signing in with an active Copilot subscription.

- Inline chat
  - Purpose: Targeted edits and explanations directly in the editor.
  - Shortcut: Trigger inline chat from the editor using the documented shortcut.
  - Behavior: Detects intent (explain, fix, refactor, etc.), gathers context, and streams suggested edits.

- Inline suggestions
  - Purpose: Intelligent next-edit predictions to accelerate typing.
  - Behavior: Ghost text suggestions and next edit suggestions help you write code faster.

- Edit mode
  - Purpose: Natural language to code transformations and edits.
  - Availability: Integrated into the chat and inline editing experiences.

Enabling and usage:
- Agent mode, inline chat, and inline suggestions are enabled by default after installation.
- The extension registers chat participants and tools that power these modes.

**Section sources**
- [README.md](file://README.md#L30-L50)
- [README.md](file://README.md#L36-L38)
- [README.md](file://README.md#L32-L35)
- [src/extension/inlineChat/node/inlineChatIntent.ts](file://src/extension/inlineChat/node/inlineChatIntent.ts#L512-L542)
- [src/extension/intents/node/allIntents.ts](file://src/extension/intents/node/allIntents.ts#L32-L52)

## Quick Start Examples
Try these common tasks to become familiar with Copilot Chat:

- Ask for a code explanation
  - In a chat session, describe what a function or class does and request an explanation.
  - The agent or chat participant will provide a concise explanation tailored to your codebase.

- Request a code change
  - Describe the desired change in natural language.
  - The agent proposes edits and applies them across files as needed.

- Use inline chat for targeted edits
  - Position your cursor or select code in the editor.
  - Use the inline chat shortcut to propose a change.
  - Review the suggested edit and accept or refine as needed.

- Switch between modes
  - Use the chat panel for broader conversations and agent mode for autonomous tasks.
  - Use inline chat for immediate, precise edits without leaving the editor.

These workflows are supported by the chat participants and intents registered by the extension.

**Section sources**
- [README.md](file://README.md#L30-L50)
- [src/extension/intents/node/allIntents.ts](file://src/extension/intents/node/allIntents.ts#L32-L52)

## Initial Configuration and Customization
Tailor Copilot Chat to your workflow with the following options:

- Custom instructions
  - Provide project-wide or task-specific context and coding guidelines to guide the AI’s responses.

- Agent skills and custom agents
  - Teach Copilot specialized capabilities with agent skills or define custom agents for specific roles.

- MCP servers and tools
  - Connect external tools and services to extend agent capabilities.

- Settings and preferences
  - Adjust settings to control behavior, enable/disable features, and tune performance.

These capabilities are exposed through the extension’s settings and tool integrations.

**Section sources**
- [README.md](file://README.md#L41-L50)
- [.github/copilot-instructions.md](file://.github/copilot-instructions.md#L262-L279)

## Troubleshooting Guide
If you encounter issues during setup or usage:

- Verify subscription and sign-in
  - Ensure your GitHub Copilot subscription is active and signed in within VS Code.

- Compatibility check
  - Confirm your VS Code version meets the minimum requirement enforced by the extension.
  - The extension prevents activation when using pre-release builds on stable VS Code channels and sets a context flag to guide users.

- Debugging requests
  - Use the “Show Chat Debug View” command to inspect requests, prompts, tools, and responses.
  - Export logs for review or sharing when seeking support.

- Telemetry and privacy
  - The extension collects usage data to improve products and services. You can adjust telemetry settings in VS Code.

- Common setup issues
  - If the extension fails to activate, ensure your VS Code version satisfies the engines constraint.
  - If inline chat does not respond, confirm the shortcut and that the editor context is selected.

**Section sources**
- [README.md](file://README.md#L12-L17)
- [README.md](file://README.md#L55-L60)
- [src/extension/extension/vscode/extension.ts](file://src/extension/extension/vscode/extension.ts#L41-L50)
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L300-L308)

## Conclusion
You are now ready to use GitHub Copilot Chat in VS Code. Start with a chat session, try inline chat for quick edits, and explore agent mode for autonomous tasks. Customize the experience with instructions, skills, and tools, and use the troubleshooting tips to resolve common issues. For deeper guidance, consult the official Copilot documentation links provided in the repository.