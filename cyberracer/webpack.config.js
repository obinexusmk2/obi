const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  mode: 'production',
  entry: './frontend/js/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'frontend/dist'),
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'frontend/index-webpack.html', to: 'index.html' },
        { from: 'assets', to: 'assets' }
      ]
    })
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'frontend')
    },
    compress: true,
    port: 8000,
    hot: true,
    historyApiFallback: true
  }
};
