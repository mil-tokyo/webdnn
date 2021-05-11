module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/separateBuild/operatorWebGL.ts',

  output: {
    filename: 'op-webgl.js',
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