declare function importScripts(path: string): void;
declare let toolbox: {
    precache: (...args: any[]) => any
    router: {
        get: (...args: any[]) => any
    }
    networkFirst: any,
    cacheFirst: any
};

importScripts('/sw-toolbox.js');

toolbox.precache(['/',
    '/models/resnet50/weight_webassembly.bin',
    '/models/neural_style_transfer/weight_webassembly.bin',
]);
toolbox.router.get('/(.*)\.bin', toolbox.cacheFirst);
