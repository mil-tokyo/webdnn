namespace WebDNN {
    function defaultFetchDelegate(input: RequestInfo, init?: RequestInit) {
        return fetch(input, init);
    }

    let fetchDelegate: (input: RequestInfo, init?: RequestInit) => Promise<Response> = defaultFetchDelegate;

    export function registerFetchDelegate(delegate: (input: RequestInfo, init?: RequestInit) => Promise<Response>) {
        fetchDelegate = delegate;
    }

    export function fetch(input: RequestInfo, init?: RequestInit) {
        return fetchDelegate(input, init);
    }
}
