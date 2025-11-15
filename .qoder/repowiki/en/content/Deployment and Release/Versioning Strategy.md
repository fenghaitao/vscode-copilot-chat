# Versioning Strategy

<cite>
**Referenced Files in This Document**   
- [package.json](file://package.json)
- [package-lock.json](file://package-lock.json)
- [tsconfig.json](file://tsconfig.json)
- [chat-lib/package.json](file://chat-lib/package.json)
- [chat-lib/package-lock.json](file://chat-lib/package-lock.json)
- [tsconfig.base.json](file://tsconfig.base.json)
- [README.md](file://README.md)
- [script/build/extractChatLib.ts](file://script/build/extractChatLib.ts)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Version Management in package.json](#version-management-in-packagejson)
3. [Dependency Management in package-lock.json](#dependency-management-in-packagelockjson)
4. [TypeScript Configuration and Version Compatibility](#typescript-configuration-and-version-compatibility)
5. [Version Increment Policies](#version-increment-policies)
6. [Extension Updates and User Experience](#extension-updates-and-user-experience)
7. [Version Compatibility Requirements](#version-compatibility-requirements)
8. [Internal Component Versioning](#internal-component-versioning)
9. [Breaking Changes Communication](#breaking-changes-communication)
10. [Build Process and Version Synchronization](#build-process-and-version-synchronization)

## Introduction
The GitHub Copilot Chat extension follows a comprehensive versioning strategy that ensures compatibility, stability, and seamless updates across its ecosystem. This document details the versioning approach used in the project, focusing on semantic versioning principles, dependency management, and compatibility requirements. The strategy encompasses package version management, TypeScript configuration, extension updates, and communication of breaking changes to ensure a consistent user experience across different VS Code versions and Node.js runtimes.

## Version Management in package.json
The GitHub Copilot Chat extension uses semantic versioning (SemVer) in its package.json file to manage version numbers and communicate the nature of changes between releases. The current version is specified in the "version" field, with the latest release being 0.33.0. The package.json file also includes several version-related fields that are critical to the extension's functionality and compatibility.

The "engines" field specifies the required versions of VS Code, npm, and Node.js that the extension supports. Currently, the extension requires VS Code version ^1.106.0-20251024, npm >=9.0.0, and Node.js >=22.14.0. This ensures that users have the necessary runtime environment to run the extension properly.

The package.json also includes a "completionsCoreVersion" field set to "1.378.1799", which tracks the version of the core completions functionality. This allows for independent versioning of specific components within the extension. Additionally, the file contains various API keys and identifiers that are used for telemetry and service integration.

**Section sources**
- [package.json](file://package.json#L1-L800)

## Dependency Management in package-lock.json
The package-lock.json file maintains a precise record of all dependencies and their versions, ensuring consistent installations across different environments. The lockfile uses version 3 format and includes both direct and transitive dependencies with their resolved versions and integrity checksums.

Dependencies are categorized into production dependencies and development dependencies. Production dependencies include essential packages such as @anthropic-ai/claude-code (^1.0.120), @anthropic-ai/sdk (^0.63.0), @github/copilot (^0.0.343), and @vscode/copilot-api (^0.1.13). These packages provide core functionality for AI integration, API access, and VS Code extension capabilities.

Development dependencies include testing frameworks (mocha, vitest), build tools (esbuild, typescript), and linting utilities (eslint, @typescript-eslint/eslint-plugin). These tools are used during development and testing but are not included in the production build.

The package-lock.json also specifies engine requirements that match those in package.json, ensuring that the correct Node.js and npm versions are used during installation. This prevents compatibility issues that could arise from using incompatible package manager versions.

**Section sources**
- [package-lock.json](file://package-lock.json#L1-L800)

## TypeScript Configuration and Version Compatibility
The TypeScript configuration in tsconfig.json extends the base configuration from tsconfig.base.json and includes settings specific to the extension's needs. The base configuration sets compiler options such as target (es2022), module (commonjs), and strict type checking, ensuring code quality and compatibility with modern JavaScript features.

The main tsconfig.json file extends the base configuration and adds specific settings for the extension, including JSX support with custom factory functions (vscpp and vscppf) and type definitions for various modules. The configuration includes types for minimist, mocha, node, picomatch, sinon, tar, and vscode, ensuring proper type checking for these dependencies.

The TypeScript configuration also includes path mappings that resolve the "vscode" module to a shim implementation during testing, allowing for better test isolation and mocking. This approach enables comprehensive testing of extension functionality without requiring a full VS Code environment.

The project uses TypeScript 5.8.3, which provides modern language features and improved type checking capabilities. This version is specified in both package.json and package-lock.json to ensure consistency across development environments.

**Section sources**
- [tsconfig.json](file://tsconfig.json#L1-L39)
- [tsconfig.base.json](file://tsconfig.base.json#L1-L23)

## Version Increment Policies
The GitHub Copilot Chat extension follows semantic versioning principles for version increments, with clear policies for major, minor, and patch releases based on the nature of changes introduced.

Major version increments (e.g., 0.x.x to 1.x.x) are reserved for significant architectural changes, breaking API changes, or major feature overhauls that could affect existing functionality. These releases require careful planning and extensive testing to ensure backward compatibility or provide appropriate migration paths.

Minor version increments (e.g., 0.32.x to 0.33.x) are used for feature additions that maintain backward compatibility. These releases include new functionality, enhancements to existing features, and improvements to user experience without breaking existing integrations or workflows.

Patch version increments (e.g., 0.33.0 to 0.33.1) are reserved for bug fixes, security patches, and minor improvements that do not introduce new features. These releases focus on stability, performance, and addressing issues reported by users.

The versioning strategy also considers the impact of model updates from the Copilot service. As mentioned in the README, even minor model upgrades require prompt changes and fixes in the extension, necessitating version updates to maintain optimal functionality.

**Section sources**
- [package.json](file://package.json#L1-L800)
- [README.md](file://README.md#L1-L84)

## Extension Updates and User Experience
The extension update process is designed to provide a seamless user experience while ensuring compatibility and stability. As mentioned in the README, Copilot Chat releases in lockstep with VS Code due to its deep UI integration, meaning each new version of Copilot Chat is only compatible with the latest release of VS Code.

This synchronization ensures that the extension can leverage the latest VS Code features and APIs while maintaining a consistent user experience. Users are encouraged to keep both VS Code and the Copilot Chat extension updated to access the latest features, security fixes, and performance improvements.

The update process is automated through the VS Code marketplace, with users receiving notifications when new versions are available. The extension respects VS Code's extension management system, allowing users to control update preferences and review release notes before installing updates.

The versioning strategy also considers the user experience during the update process. Breaking changes are minimized, and when necessary, are accompanied by clear migration guidance and deprecation warnings in earlier releases to give users time to adapt.

**Section sources**
- [README.md](file://README.md#L1-L84)

## Version Compatibility Requirements
The GitHub Copilot Chat extension has specific compatibility requirements for VS Code versions and Node.js runtimes to ensure proper functionality and stability. As stated in the README, the extension is only compatible with the latest and newest release of VS Code due to its deep UI integration.

The package.json file specifies the required VS Code version as ^1.106.0-20251024, which means the extension requires VS Code version 1.106.0 or higher, up to but not including version 2.0.0. This version constraint ensures that the extension can use the latest VS Code APIs and features while maintaining backward compatibility within the 1.x series.

For the Node.js runtime, the extension requires version >=22.14.0, which provides the necessary JavaScript engine features and performance characteristics for the extension's functionality. This version requirement is specified in both package.json and package-lock.json to ensure consistency across development and production environments.

The extension also has compatibility requirements for npm, requiring version >=9.0.0. This ensures that users have a package manager with the necessary features and performance characteristics to install and manage the extension's dependencies.

**Section sources**
- [package.json](file://package.json#L1-L800)
- [README.md](file://README.md#L1-L84)

## Internal Component Versioning
The GitHub Copilot Chat extension includes internal components with their own versioning strategies, particularly evident in the chat-lib subdirectory. The chat-lib package, located in the chat-lib directory, has its own package.json and package-lock.json files, allowing it to manage dependencies and versions independently.

The chat-lib package.json specifies a version of "0.0.0", indicating that it is not intended to be published as a standalone package but rather used internally within the extension. This approach allows the team to extract and reuse chat functionality without exposing it as a public API.

The chat-lib package has its own set of dependencies, including @microsoft/tiktokenizer (^1.0.10), @vscode/copilot-api (^0.1.12), and openai (^5.11.0), which may have different version requirements than the main extension. This separation allows for more flexible dependency management and reduces the risk of version conflicts.

The build process, as implemented in script/build/extractChatLib.ts, synchronizes dependencies between the main extension and the chat-lib component, ensuring that both use compatible versions of shared packages. This process helps maintain consistency across the codebase while allowing for independent development of internal components.

**Section sources**
- [chat-lib/package.json](file://chat-lib/package.json#L1-L63)
- [chat-lib/package-lock.json](file://chat-lib/package-lock.json#L1-L800)
- [script/build/extractChatLib.ts](file://script/build/extractChatLib.ts#L1-L608)

## Breaking Changes Communication
The GitHub Copilot Chat team follows a structured approach to communicating breaking changes to users and developers. As the extension is tightly integrated with VS Code and releases in lockstep with it, breaking changes are minimized and carefully planned.

When breaking changes are necessary, they are typically introduced in major version releases, with clear documentation and migration guidance provided in the release notes. The team leverages the VS Code marketplace's release notes feature to communicate changes, improvements, and known issues for each release.

For developers using the extension's APIs, deprecation warnings are added in earlier releases to provide advance notice of upcoming changes. This allows developers time to update their code and adapt to new patterns before the deprecated functionality is removed.

The team also maintains transparency through the README and documentation, providing information about the extension's capabilities, limitations, and usage guidelines. The transparency note mentioned in the README helps users understand the technical preview nature of certain features and how to provide feedback for improvement.

**Section sources**
- [README.md](file://README.md#L1-L84)

## Build Process and Version Synchronization
The build process for GitHub Copilot Chat includes mechanisms for version synchronization and dependency management, as evidenced by the extractChatLib.ts script in the script/build directory. This script is responsible for extracting the chat-lib component from the main codebase and ensuring that its dependencies are synchronized with the main extension.

The extractChatLib.ts script performs several key functions related to version management:
1. It copies the root package.json to the chat-lib/src directory
2. It updates chat-lib dependencies to match versions in the root package.json
3. It synchronizes package-lock.json entries for changed dependencies and their transitive dependencies
4. It validates the extracted module through TypeScript compilation

This process ensures that the chat-lib component uses compatible versions of shared packages, reducing the risk of version conflicts and ensuring consistent behavior across the codebase. The script also handles the transformation of import paths and module references to maintain proper module resolution after extraction.

The build process also includes TypeScript compilation as a validation step, ensuring that the extracted code is type-correct and free of compilation errors. This helps catch version-related issues early in the development process, before they can affect users.

**Section sources**
- [script/build/extractChatLib.ts](file://script/build/extractChatLib.ts#L1-L608)