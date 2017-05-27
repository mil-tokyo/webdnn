const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const {CheckerPlugin} = require('awesome-typescript-loader');
const HTMLWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HtmlWebpackInlineSourcePlugin = require('html-webpack-inline-source-plugin');

const path = require('path');

const minifyOption = {
	collapseBooleanAttributes: true,
	collapseInlineTagWhitespace: true,
	collapseWhitespace: true,
	removeAttributeQuotes: true,
	removeComments: true,
	removeEmptyAttributes: true,
	removeOptionalTags: true,
	removeRedundantAttributes: true,
	removeScriptTypeAttributes: true,
	removeTagWhitespace: true
};

module.exports = {
	entry: {
		'index': './src/scripts/index.ts',
		'resnet50': './src/scripts/resnet50.ts',
		'neural_style_transfer': './src/scripts/neural_style_transfer.ts',
		'sw': './src/scripts/sw.ts',
	},
	output: {
		path: path.resolve(__dirname, './build/webdnn'),
		filename: '[name].js'
	},
	module: {
		rules: [{
			test: /\.tsx?$/,
			use: [{
				loader: 'awesome-typescript-loader',
			}]
		}, {
			test: /\.scss?$/,
			use: ExtractTextPlugin.extract({
				fallback: 'style-loader',
				use: ['css-loader', 'postcss-loader', 'sass-loader']
			})
		}]
	},
	resolve: {
		modules: [
			path.join(__dirname, './src'),
			path.join(__dirname, './node_modules'),
		],
		extensions: ['.ts', '.tsx', '.js', '.jsx', '.scss']
	},
	plugins: [
		new ExtractTextPlugin({
			filename: getPath => getPath('[name].css'),
			allChunks: true
		}),
		new CheckerPlugin(),
		new CopyWebpackPlugin([{
			from: './src/static',
			to: './'
		}]),
		new HTMLWebpackPlugin({
			filename: 'index_ja.html',
			template: 'src/html/index_ja.html',
			chunks: ['index'],
			inlineSource: '.(js|css)$',
			minify: minifyOption
		}),
		new HTMLWebpackPlugin({
			filename: 'index.html',
			template: 'src/html/index.html',
			chunks: ['index'],
			inlineSource: '.(js|css)$',
			minify: minifyOption
		}),
		new HTMLWebpackPlugin({
			filename: 'resnet50.html',
			template: 'src/html/resnet50.html',
			chunks: ['resnet50'],
			inlineSource: '.(js|css)$',
			minify: minifyOption
		}),
		new HTMLWebpackPlugin({
			filename: 'neural_style_transfer.html',
			template: 'src/html/neural_style_transfer.html',
			chunks: ['neural_style_transfer'],
			inlineSource: '.(js|css)$',
			minify: minifyOption
		}),
		new UglifyJSPlugin(),
		new HtmlWebpackInlineSourcePlugin()
	]
};
