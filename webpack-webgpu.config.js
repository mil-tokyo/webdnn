module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/separateBuild/operatorWebGPU.ts',

  output: {
    filename: 'op-webgpu.js',
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