const path = require('path');
const MinifyPlugin = require('babel-minify-webpack-plugin');

module.exports = {
    mode: 'production',
    entry: path.join(__dirname, './webdnn.js'),
    output: {
        filename: 'webdnn.js',
        path: path.join(__dirname, '../../dist'),
        library: 'WebDNN',
        libraryTarget: 'umd'
    },
    // devtool: 'source-map',
    plugins: [
        new MinifyPlugin()
    ]
};
