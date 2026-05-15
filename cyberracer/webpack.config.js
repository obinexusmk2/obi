const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: './frontend/js/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'frontend/dist'),
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'frontend/index.html', to: 'index.html' },
        { from: 'assets', to: 'assets' }
      ]
    })
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'frontend'),
    },
    compress: true,
    port: 8000,
    hot: true,
    historyApiFallback: true
  },
  mode: 'development'
};
