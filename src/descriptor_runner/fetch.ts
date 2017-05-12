/// <reference path="./util/dispatch_scheduler.ts" />

namespace WebDNN {
    /**
     * Fetch delegate function.
     * Every fetch call in WebDNN is delegated to this function.
     * As default, `window.fetch` is set.
     * @type {(input:RequestInfo, init?:RequestInit)=>Promise<Response>}
     */
    let fetchDelegate: (input: RequestInfo, init?: RequestInit) => Promise<Response> = window.fetch;

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
     * @returns Response
     */
    export function fetch(input: RequestInfo, init?: RequestInit) {
        return fetchDelegate(input, init);
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
