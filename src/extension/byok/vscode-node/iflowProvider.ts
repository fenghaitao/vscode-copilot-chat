/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
import { ILogService } from '../../../platform/log/common/logService';
import { IFetcherService } from '../../../platform/networking/common/fetcherService';
import { IInstantiationService } from '../../../util/vs/platform/instantiation/common/instantiation';
import { BYOKAuthType, BYOKKnownModels } from '../common/byokProvider';
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
	constructor(
		knownModels: BYOKKnownModels,
		byokStorageService: IBYOKStorageService,
		@IFetcherService _fetcherService: IFetcherService,
		@ILogService _logService: ILogService,
		@IInstantiationService _instantiationService: IInstantiationService,
	) {
		// Merge CDN models with default models, with CDN taking precedence
		const mergedModels = { ...defaultIflowModels, ...knownModels };
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
	}
}
