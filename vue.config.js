const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: 'static/dist',
  publicPath: '/static/dist/',
  configureWebpack: {
    devtool: 'source-map'
  }
})