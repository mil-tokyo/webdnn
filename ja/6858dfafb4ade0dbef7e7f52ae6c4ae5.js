importScripts('/webdnn/sw-toolbox.js');

const VERSION = 6;

toolbox.precache(['/',
	`https://mil-tokyo.github.io/webdnn-data/models/resnet/weight_webassembly.bin?raw=true&v=${VERSION}`,
	`https://mil-tokyo.github.io/webdnn-data/models/resnet/weight_webgpu.bin?raw=true&v=${VERSION}`,
	`https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/weight_webassembly.bin?raw=true&v=${VERSION}`,
	`https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/weight_webgpu.bin?raw=true&v=${VERSION}`
]);
toolbox.router.get('/(.*)\.bin', toolbox.cacheFirst);
