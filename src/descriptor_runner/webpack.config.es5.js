const path = require('path');
const MinifyPlugin = require('babel-minify-webpack-plugin');

module.exports = {
    entry: path.join(__dirname, './webdnn.js'),
    output: {
        filename: 'webdnn.es5.js',
        path: path.join(__dirname, '../../dist'),
        library: 'WebDNN',
        libraryTarget: 'umd'
    },
    devtool: 'source-map',
    plugins: [
        new MinifyPlugin()
    ]
};
