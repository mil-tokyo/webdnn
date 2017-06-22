declare function importScripts(path: string): void;
declare let toolbox: {
    precache: (...args: any[]) => any
    router: {
        get: (...args: any[]) => any
    }
    networkFirst: any,
    cacheFirst: any
};

importScripts('/webdnn/sw-toolbox.js');

toolbox.precache(['/',
    'https://mil-tokyo.github.io/webdnn-data/models/resnet50/weight_webassembly.bin?raw=true&v=3',
    'https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/weight_webassembly.bin?raw=true&v=3',
]);
toolbox.router.get('/(.*)\.bin', toolbox.cacheFirst);
