/**
 * @module webdnn
 * @preferred
 *
 * Module `WebDNN` provides main features of WebDNN.
 */
/** Don't Remove This comment block */
/// <reference path="./webgpu.d.ts" />
import { DescriptorRunner as DescriptorRunnerGeneric, DescriptorRunnerConstructor } from "./descriptor_runner/descriptor_runner";
import DescriptorRunnerFallback from "./descriptor_runner/descriptor_runner_fallback";
import DescriptorRunnerWebassembly from "./descriptor_runner/descriptor_runner_webassembly";
import DescriptorRunnerWebGL from "./descriptor_runner/descriptor_runner_webgl";
import DescriptorRunnerWebGPU from "./descriptor_runner/descriptor_runner_webgpu";
import { registerTransformUrlDelegate } from "./fetch";
import { GraphDescriptor } from "./graph_descriptor/graph_descriptor";
import * as Image from "./image";
import * as Math from "./math";


/**
 * DEBUG flag for developing WebDNN
 * @private
 */
let configurations: { [key: string]: any } = {};

/**
 * get configuration
 * @private
 */
export function getConfiguration<T>(key: string, defaultValue?: T): T {
    return key in configurations ? configurations[key] : defaultValue;
}

/**
 * set configuration
 * @private
 */
export function setConfiguration(key: string, value: any) {
    configurations[key] = value
}

/**
 * Backend names supported in WebDNN
 */
export type BackendName = 'webgpu' | 'webgl' | 'webassembly' | 'fallback';

/**
 * Descriptor runner
 */
export type DescriptorRunner = DescriptorRunnerGeneric<GraphDescriptor, any>;

/**
 * Backend constructor map
 * @private
 */
const descriptorRunners: { [k in BackendName]: DescriptorRunnerConstructor<GraphDescriptor, any> } = {
    webgpu: DescriptorRunnerWebGPU,
    webgl: DescriptorRunnerWebGL,
    webassembly: DescriptorRunnerWebassembly,
    fallback: DescriptorRunnerFallback
};

/**
 * Result structure of [[getBackendAvailability|`WebDNN.getBackendAvailability`]]
 */
export interface BackendAvailability {
    /**
     * Whether each backend is available or not.
     *
     * ### Example
     *
     * ```ts
     * WebDNN.getBackendAvailability().status
     * >>> {
     *   'webgpu': false,
     *   'webassembly': true,
     *   'webgl': true,
     *   'fallback': true
     * }
     * ```
     */
    status: { [name in BackendName]: boolean },

    /**
     * Default backend order WebDNN try to use
     *
     * ### Examples
     *
     * ```ts
     * WebDNN.getBackendAvailability().defaultOrder
     * >>> ['webassembly', 'webgl', 'fallback']
     * ```
     */
    defaultOrder: BackendName[]
}

/**
 * Check each computing backend is available or not in this browser.
 * The result will be returned as [[BackendAvailability|`BackendAvailability`]] structure.
 *
 * @returns backend availability
 */
export function getBackendAvailability(): BackendAvailability {
    let status: { [name in BackendName]: boolean } = {
        'webgpu': descriptorRunners['webgpu'].checkAvailability(),
        'webgl': descriptorRunners['webgl'].checkAvailability(),
        'webassembly': descriptorRunners['webassembly'].checkAvailability(),
        'fallback': descriptorRunners['fallback'].checkAvailability(),
    };

    let order = (['webgpu', 'webgl', 'webassembly', 'fallback'] as BackendName[]).filter(backend => status[backend]);

    return {
        status: status,
        defaultOrder: order
    }
}

/**
 * Initialize specified backend
 * @private
 */
async function initBackend(backendName: BackendName, option?: any): Promise<DescriptorRunner | null> {
    if (!(backendName in descriptorRunners)) throw new Error(`Unknown backend: "${backendName}"`);

    let runner: DescriptorRunner;

    try {
        runner = new descriptorRunners[backendName](option);
        await runner.init();
    } catch (ex) {
        console.warn(`Failed to initialize ${backendName} backend: ${ex}`);
        return null;
    }

    return runner;
}

/**
 * Option structure of [[load|`WebDNN.load`]]
 */
export interface InitOption {
    /**
     * The order of backend names to be initialized.
     */
    backendOrder?: BackendName | (BackendName[]),

    /**
     * Backend-specific options. Currently (v1.3), this option has no effect.
     */
    backendOptions?: { [key: string]: any },

    /**
     * Callback function which is called to notice the progress status of loading binary data.
     *
     * Currently Streaming fetch feature is not perfectly supported in browsers. Therefore, this option will be
     * ignored in some web browsers.
     *
     * ### Examples
     *
     * ```js
     * let runner = await WebDNN.load('./model', {
     *     progressCallback: (loaded, total) => console.log(`${ (loaded/total*100).toFixed(1) }% Loaded`);
     * });
     * ```
     */
    progressCallback?: (loaded: number, total: number) => any,

    /**
     * URL of directory that contains weight binary files.
     *
     * If both
     * [[InitOption.weightDirectory|`InitOption.weightDirectory`]] and
     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are specified,
     * At first, all urls of binary weights' are replaced by [[InitOption.weightDirectory|`InitOption.weightDirectory`]], and then
     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are applied.
     *
     * ### Examples
     *
     * ```js
     * // Graph descriptor JSON file will be loaded from 'original.host.com/model', and
     * // model binary data will be loaded from 'custom.host.com/model'.
     * WebDNN.load('https://original.host.com/model', {
     *     weightDirectory: 'https://custom.host.com/model'
     * });
     * ```
     */
    weightDirectory?: string,

    /**
     * Delegate function which will be called with original url, and must return converted url strings.
     * This function is called before WebDNN fetch any data (descriptor json file, and binary data)
     * You can modified url to fetch data from other domain, for example.
     *
     * If both
     * [[InitOption.weightDirectory|`InitOption.weightDirectory`]] and
     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are specified,
     * At first, all urls of binary weights' are replaced by [[InitOption.weightDirectory|`InitOption.weightDirectory`]], and then
     * [[InitOption.transformUrlDelegate|`InitOption.transformUrlDelegate`]] are applied.
     *
     * ### Examples
     *
     * Fetch binary data from other domain
     *
     * ```js
     * // Graph descriptor JSON file will be loaded from 'original.host.com/model', and
     * // model binary data will be loaded from 'custom.host.com/model'.
     * WebDNN.load('https://original.host.com/model', {
     *     transformUrlDelegate: (url) => {
     *         if ((/\.bin/).test(url)) {
     *             url = url.replace('original.host.com', 'custom.host.com');
     *         }
     *         return url;
     *     }
     * });
     * ```
     */
    transformUrlDelegate?: (url: string) => string,

    /**
     * WebDNN cache strategy. One of follows is available.
     *
     * - `latest` (default)
     *
     *  Fetch `descriptor.json` at first and check whether assets in server is same as cached assets. If it's same, use cached assets,
     *  otherwise, fetch all assets and replace cached assets.
     *
     * - `networkFirst`
     *
     *  Fetch all asset files. If it succeeds, use fetched assets. If failed, use cached assets if exist, otherwise, an error is thrown.
     *
     * - `cacheFirst`
     *
     *  If cache is exist, use cache, otherwise, fetch assets. If it failed, an error is thrown.
     *
     * - `networkOnly`
     *
     *  Fetch all asset files. If failed, an error is thrown.
     *
     * - `cacheOnly`
     *
     *  If cache is exist, use cache, otherwise, an error is thrown.
     *
     */
    cacheStrategy?: 'latest' | 'networkFirst' | 'cacheFirst' | 'networkOnly' | 'cacheOnly',

    /**
     * If true, WebDNN save fetched parameter data cache in available `WebStorage`. As default, it's `true`.
     */
    saveCache?: boolean
}

/**
 * Initialize descriptor runner. This function performs follow things.
 *
 * 1. Try to initialize computing backend. WebDNN will try to initialize each backend in order of
 *    the result of [[getBackendAvailability|`getBackendAvailability`]].
 *    If you want to modify this order, specify [[InitOption.backendOrder|`initOption.backendOrder`]] option.
 *
 * 2. Load model data based on initialized backend. Generally, DNN binary data is very large and it takes long time to load.
 *    [[InitOption.progressCallback|`initOption.progressCallback`]] option provides the progress status of loading.
 *
 * ### Examples
 *
 * - Basic usage
 *
 *   ```js
 *   let runner = await WebDNN.load('./model');
 *   ```
 *
 * - With `initOption.progressCallback` option
 *
 *   ```js
 *   let runner = await WebDNN.load('./model', {
 *       progressCallback: (loaded, total) => console.log(`${ (loaded/total*100).toFixed(1) }% Loaded`);
 *   });
 *   ```
 *
 * @param directory URL of directory that contains graph descriptor files (e.g. graph_webgpu.json)
 * @param initOption Initialize option
 * @return DescriptorRunner instance, which is the interface to input/output data and run the model.
 */
export async function load(directory: string, initOption: InitOption = {}): Promise<DescriptorRunner> {
    let {
        backendOrder = null,
        backendOptions = {},
        cacheStrategy = 'latest',
        saveCache = true,
        progressCallback,
        weightDirectory,
        transformUrlDelegate
    } = initOption;

    if (!backendOrder) backendOrder = getBackendAvailability().defaultOrder;
    if (typeof backendOrder === 'string') backendOrder = [backendOrder];
    backendOrder = backendOrder.slice();
    if (backendOrder.indexOf('fallback') === -1) backendOrder.concat(['fallback']);

    registerTransformUrlDelegate((url) => {
        if (weightDirectory) {
            if ((/\.bin/).test(url)) {
                url = url.replace(directory, weightDirectory);
            }
        }
        if (transformUrlDelegate) url = transformUrlDelegate(url);
        return url;
    });

    while (backendOrder.length > 0) {
        let backendName = backendOrder.shift()!;
        let runner: (DescriptorRunner | null) = await initBackend(backendName, backendOptions[backendName]);
        if (!runner) continue;

        try {
            let descriptor: GraphDescriptor;
            let parameters: any;
            let fetchedDescriptor: GraphDescriptor | null;
            let cachedDescriptor: GraphDescriptor | null;


            switch (cacheStrategy) {
                case 'latest':
                    fetchedDescriptor = await runner.fetchDescriptor(directory).catch(() => null);
                    cachedDescriptor = await runner.restoreCachedDescriptor(directory);

                    if (cachedDescriptor && fetchedDescriptor && cachedDescriptor.converted_at === fetchedDescriptor.converted_at) {
                        descriptor = cachedDescriptor;
                        parameters = await runner.restoreCachedParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    if (fetchedDescriptor) {
                        descriptor = fetchedDescriptor;
                        parameters = await runner.fetchParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    if (cachedDescriptor) {
                        descriptor = cachedDescriptor;
                        parameters = await runner.restoreCachedParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    throw Error('Network error is occurred and no cache is exist.');

                case 'networkOnly':
                case 'networkFirst':
                    fetchedDescriptor = await runner.fetchDescriptor(directory).catch(() => null);
                    if (fetchedDescriptor) {
                        descriptor = fetchedDescriptor;
                        parameters = await runner.fetchParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    if (cacheStrategy === 'networkOnly') throw Error('Network error is occurred in "networkOnly" cache strategy');

                    cachedDescriptor = await runner.restoreCachedDescriptor(directory);
                    if (cachedDescriptor) {
                        descriptor = cachedDescriptor;
                        parameters = await runner.restoreCachedParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    throw Error('Network error is occurred and no cache is exist.');

                case 'cacheOnly':
                case 'cacheFirst':
                    cachedDescriptor = await runner.restoreCachedDescriptor(directory);
                    if (cachedDescriptor) {
                        descriptor = cachedDescriptor;
                        parameters = await runner.restoreCachedParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    if (cacheStrategy === 'cacheOnly') throw Error('No cache is exist in "cacheOnly" cache strategy');

                    fetchedDescriptor = await runner.fetchDescriptor(directory).catch(() => null);
                    if (fetchedDescriptor) {
                        descriptor = fetchedDescriptor;
                        parameters = await runner.fetchParameters(directory, progressCallback);
                        if (parameters) break;
                    }

                    throw Error('Network error is occurred and no cache is exist.');

                default:
                    throw Error(`"${cacheStrategy}" is not valid cache strategy name: "latest", "networkFirst", "networkOnly", "cacheFirst", "cacheOnly" is available.`)
            }

            await runner.setDescriptorAndParameters(descriptor, parameters);

            if (saveCache) {
                try {
                    await runner.saveCache(directory, descriptor, parameters);
                } catch (e) {
                    /* do nothing */
                }
            }
        } catch (ex) {
            console.warn(`Model loading failed for ${backendName} backend. Trying next backend: ${ex.message}`);
            continue;
        }

        return runner;
    }

    throw new Error('No backend is available');
}

export { GraphDescriptor }

// Export support (not-dependent) functions
export { Math, Image }
