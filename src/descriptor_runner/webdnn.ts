/**
 * @module webdnn
 * @preferred
 *
 * Module `WebDNN` provides main features of WebDNN.
 */
/** Don't Remove This comment block */
/// <reference path="./webgpu.d.ts" />
import { DescriptorRunner, DescriptorRunnerConstructor } from "./descriptor_runner/descriptor_runner";
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
let DEBUG: boolean = false;

/**
 * get DEBUG flag for developing WebDNN
 * @private
 */
export function isDebugMode() {
    return DEBUG;
}

/**
 * set DEBUG flag for developing WebDNN
 * @private
 */
export function setDebugMode(flag) {
    DEBUG = flag;
}

/**
 * Backend names supported in WebDNN
 */
export type BackendName = 'webgpu' | 'webgl' | 'webassembly' | 'fallback';

/**
 * Backend constructor map
 * @private
 */
const descriptorRunners: { [k in BackendName]: DescriptorRunnerConstructor<GraphDescriptor> } = {
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

    let order = (['webgpu', 'webassembly', 'webgl', 'fallback'] as BackendName[]).filter(backend => status[backend]);

    return {
        status: status,
        defaultOrder: order
    }
}

/**
 * Initialize specified backend
 * @private
 */
async function initBackend(backendName: BackendName, option?: any): Promise<DescriptorRunner<GraphDescriptor> | null> {
    if (!(backendName in descriptorRunners)) throw new Error(`Unknown backend: "${backendName}"`);

    let runner: DescriptorRunner<GraphDescriptor>;

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
     * If true, WebDNN fetches binary data even if the data is already cached (append tiestamp to request url).
     * Otherwise, WebDNN fetches same URL and generally browser cache is used.
     */
    ignoreCache?: boolean,

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
    transformUrlDelegate?: (url: string) => string
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
export async function load(directory: string, initOption: InitOption = {}): Promise<DescriptorRunner<GraphDescriptor>> {
    let backendOrder = initOption.backendOrder;
    if (!backendOrder) {
        backendOrder = getBackendAvailability().defaultOrder;
    } else if (typeof backendOrder === 'string') {
        backendOrder = [backendOrder];
    }
    backendOrder = backendOrder.slice();
    if (backendOrder.indexOf('fallback') === -1) backendOrder.concat(['fallback']);

    registerTransformUrlDelegate((url) => {
        if (initOption.weightDirectory) {
            if ((/\.bin/).test(url)) {
                url = url.replace(directory, initOption.weightDirectory);
            }
        }
        if (initOption.transformUrlDelegate) {
            url = initOption.transformUrlDelegate(url);
        }
        return url;
    });

    let backendOptions = initOption.backendOptions || {};

    while (backendOrder.length > 0) {
        let backendName = backendOrder.shift()!;
        let runner: (DescriptorRunner<GraphDescriptor> | null) = await initBackend(backendName, backendOptions[backendName]);
        if (!runner) continue;
        runner.ignoreCache = Boolean(initOption.ignoreCache);

        try {
            await runner.load(directory, initOption.progressCallback);
        } catch (ex) {
            console.warn(`Model loading failed for ${backendName} backend. Trying next backend: ${ex.message}`);
            continue;
        }

        return runner;
    }

    throw new Error('No backend is available');
}

export { DescriptorRunner, GraphDescriptor }

// Export support (not-dependent) functions
export { Math, Image }
