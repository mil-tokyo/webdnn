module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/separateBuild/coreOnly.ts',

  output: {
    filename: 'webdnn-core.js',
    path: __dirname + '/dist',
    library: 'WebDNN',
    libraryTarget: 'var'
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