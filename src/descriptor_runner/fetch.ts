/// <reference path="./util/dispatch_scheduler.ts" />

let transformDelegate: (base: string) => string = url => url;

/**
 * Fetch delegate function.
 * Every fetch call in WebDNN is delegated to this function.
 * As default, `window.fetch` is set.
 * @type {(input:RequestInfo, init?:RequestInit)=>Promise<Response>}
 */
let fetchDelegate: (input: RequestInfo, init?: RequestInit) => Promise<Response> = window.fetch;

namespace WebDNN {
    export interface WebDNNRequestInit extends RequestInit {
        ignoreCache: boolean
    }

    /**
     * Register delegate function for transform url
     * @param url url which will be transformed
     */
    export function transformUrl(url: string) {
        return transformDelegate(url);
    }

    /**
     * Register delegate function for transform url
     * @param delegate delegate function
     */
    export function registerTransformDelegate(delegate: (base: string) => string) {
        transformDelegate = delegate;
    }

    /**
     * Register delegate function for fetch
     * @param delegate delegate function
     */
    export function registerFetchDelegate(delegate: (input: RequestInfo, init?: RequestInit) => Promise<Response>) {
        fetchDelegate = delegate;
    }

    /**
     * Fetch function. WebDNN API use this fetch function instead of original fetch function.
     * @param input Requested url
     * @param init Additional information about fetch
     * @param init.ignoreCache If true, cache is ignored by appending '?t=(timestamp)' to the end of request url.
     * @returns Response
     */
    export async function fetch(input: RequestInfo, init?: WebDNNRequestInit) {
        if (typeof input == 'string') {
            input = transformUrl(input) + ((init && init.ignoreCache) ? '?t=' + Date.now() : '');
        } else {
            input = Object.assign({}, input, {
                url: transformUrl(input.url) + ((init && init.ignoreCache) ? '?t=' + Date.now() : '')
            });
        }

        let res = await fetchDelegate(input, init);
        if (!res.ok) throw new Error(`Fetch returns status code ${res.status}: ${res.statusText}`);
        return res;
    }

    /**
     * Read `Response.body` stream as ArrayBuffer. This function provide progress information by callback.
     * @param res Response object
     * @param callback Callback function.
     * @returns ArrayBuffer
     */
    export function readArrayBufferProgressively(res: Response, callback?: (loaded: number, total: number) => any): Promise<ArrayBuffer> {
        if (!callback || !res.body) return res.arrayBuffer();

        let contentLength = res.headers.get('Content-Length');
        if (!contentLength) return res.arrayBuffer();
        const total = parseInt(contentLength);

        let buffer = new Uint8Array(total);
        let loaded = 0;
        let reader = res.body.getReader();
        let callbackScheduler = new WebDNN.util.DispatchScheduler();

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
}
