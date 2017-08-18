export async function customFetch(input: RequestInfo, init?: RequestInit) {
    let res = await fetch(input, init);
    if (!res.ok) throw Error(`Network request is failed: (${res.status}) ${res.statusText}`);

    return res;
}