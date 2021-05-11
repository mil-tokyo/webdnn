module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/separateBuild/operatorWasm.ts',

  output: {
    filename: 'op-wasm.js',
    path: __dirname + '/dist',
  },

  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader'
      }
    ]
  },
  resolve: {
    extensions: [
      '.ts',
      '.js'
    ]
  }
};