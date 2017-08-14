importScripts('/webdnn/sw-toolbox.js');

toolbox.precache(['/',
	'https://mil-tokyo.github.io/webdnn-data/models/resnet/weight_webassembly.bin?raw=true&v=4',
	'https://mil-tokyo.github.io/webdnn-data/models/resnet/weight_webgpu.bin?raw=true&v=4',
	'https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/weight_webassembly.bin?raw=true&v=4',
	'https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/weight_webgpu.bin?raw=true&v=4'
]);
toolbox.router.get('/(.*)\.bin', toolbox.cacheFirst);
