module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/separateBuild/operatorWebGL.ts',

  output: {
    filename: 'op-webgl2-4096.js',
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
// Currently, webgl1 and webgl2 has same operator
// source codes and dynamically branching in each operator.
// This may change in the future.
