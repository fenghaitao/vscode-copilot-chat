/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { commands } from 'vscode';
import { ILogService } from '../../../platform/log/common/logService';
import { Disposable } from '../../../util/vs/base/common/lifecycle';
import { IExtensionContribution } from '../../common/contributions';

/**
 * Temporary test command to manually trigger iflow API key configuration
 * This is a workaround for testing when the UI management button isn't working
 */
export class TestIflowCommand extends Disposable implements IExtensionContribution {
	public readonly id: string = 'test-iflow-command';

	constructor(
		@ILogService private readonly _logService: ILogService,
	) {
		super();

		// Register a user-facing command that can be called from Command Palette
		this._register(commands.registerCommand('github.copilot.chat.testConfigureIflow', async () => {
			this._logService.info('[TestIflowCommand] Manually triggering iflow configuration');

			try {
				// Call the manageBYOK command with 'iflow' as the vendor
				await commands.executeCommand('github.copilot.chat.manageBYOK', 'iflow');
				this._logService.info('[TestIflowCommand] manageBYOK command completed');
			} catch (error) {
				this._logService.error('[TestIflowCommand] Error calling manageBYOK:', error);
			}
		}));

		this._logService.info('[TestIflowCommand] Test command registered: github.copilot.chat.testConfigureIflow');
	}
}
