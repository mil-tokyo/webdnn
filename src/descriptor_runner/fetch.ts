/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import DispatchScheduler from "./util/dispatch_scheduler";

/**
 * @protected
 */
let transformDelegate: (base: string) => string = url => url;

/**
 * @protected
 */
export interface WebDNNRequestInit extends RequestInit {
    ignoreCache: boolean
}

/**
 * Transform url generated based on current active backend
 * @param url transformed url
 * @protected
 */
export function transformUrl(url: string) {
    return transformDelegate(url);
}

/**
 * Register delegate function for transform url.
 *
 * Registered delegate function is called before WebDNN fetch any data (descriptor json file, and binary data).
 * You can modified url to fetch data from other domain, for example.
 *
 * ### Examples
 *
 * Fetch binary data from other domain
 *
 * ```js
 * // Register delegate function before loading
 * WebDNN.registerTransformUrlDelegate((url) => {
 *     if ((/\.bin/).test(url)) {
 *         url = url.replace('original.host.com', 'custom.host.com');
 *     }
 *     return url;
 * })
 *
 * // Graph descriptor JSON file will be loaded from 'original.host.com/model', and
 * // model binary data will be loaded from 'custom.host.com/model'.
 * WebDNN.load('https://original.host.com/model');
 * ```
 *
 * @param delegate Delegate function which will be called with original url, and must return converted url strings.
 */
export function registerTransformUrlDelegate(delegate: (base: string) => string) {
    transformDelegate = delegate;
}

/**
 * Fetch function. WebDNN API use this function instead of original `fetch` function.
 * FIXME
 * @param input Requested url
 * @param init Additional information about webdnnFetch
 * @param init.ignoreCache If true, cache is ignored by appending '?t=(timestamp)' to the end of request url.
 * @returns Response
 * @protected
 */
export default async function webdnnFetch(input: RequestInfo, init?: WebDNNRequestInit) {
    if (typeof input == 'string') {
        input = transformUrl(input) + ((init && init.ignoreCache) ? '?t=' + Date.now() : '');
    } else {
        input = Object.assign({}, input, {
            url: transformUrl(input.url) + ((init && init.ignoreCache) ? '?t=' + Date.now() : '')
        });
    }

    let res = await fetch(input, init);
    if (!res.ok) throw new Error(`Fetch returns status code ${res.status}: ${res.statusText}`);
    return res;
}

/**
 * Read `Response.body` stream as ArrayBuffer. This function provide progress information by callback.
 * @param res Response object
 * @param callback Callback function.
 * @returns ArrayBuffer
 * @protected
 */
export function readArrayBufferProgressively(res: Response, callback?: (loaded: number, total: number) => any): Promise<ArrayBuffer> {
    if (!callback || !res.body) return res.arrayBuffer();

    let contentLength = res.headers.get('Content-Length');
    if (!contentLength) return res.arrayBuffer();
    const total = parseInt(contentLength);

    let buffer = new Uint8Array(total);
    let loaded = 0;
    let reader = res.body.getReader();
    let callbackScheduler = new DispatchScheduler();

    function accumulateLoadedSize(chunk) {
        buffer.set(chunk.value, loaded);
        loaded += chunk.value.length;

        if (callback) {
            callbackScheduler.request(() => callback(loaded, total));
        }

        if (loaded == total) {
            callbackScheduler.forceDispatch();
            return buffer.buffer;
        } else {
            return reader.read().then(accumulateLoadedSize);
        }
    }

    return reader.read().then(accumulateLoadedSize);
}
