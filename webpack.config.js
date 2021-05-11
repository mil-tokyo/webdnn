module.exports = {
  mode: 'development',
  entry: './src/descriptor_runner/index.ts',

  output: {
    filename: 'webdnn.js',
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