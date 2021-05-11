module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/separateBuild/operatorCPU.ts',

  output: {
    filename: 'op-cpu.js',
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