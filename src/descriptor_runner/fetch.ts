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
     * @returns {Promise<Response>} Response
     */
    export function fetch(input: RequestInfo, init?: RequestInit) {
        return fetchDelegate(input, init);
    }
}
