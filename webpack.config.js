const glob = require('glob');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const { CheckerPlugin } = require('awesome-typescript-loader');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HTMLWebpackPlugin = require('html-webpack-plugin');
const HTMLWebpackInlineSourcePlugin = require('html-webpack-inline-source-plugin');
const ScriptExtHtmlWebpackPlugin = require('script-ext-html-webpack-plugin');
const PurifyCSSPlugin = require('purifycss-webpack');

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

let plugins = [
	new ExtractTextPlugin({
		filename: getPath => getPath('[name].css'),
		allChunks: true
	}),
	new PurifyCSSPlugin({
		paths: {
			'index': glob.sync(path.join(__dirname, 'src/html/index.html')),
			'resnet50': glob.sync(path.join(__dirname, 'src/html/resnet50.html')),
			'neural_style_transfer': glob.sync(path.join(__dirname, 'src/html/neural_style_transfer.html'))
		},
		minimize: true,
		purifyOptions: {
			rejected: true,
			whitelist: ['canvas']
		}
	}),
	new CheckerPlugin(),
	new UglifyJSPlugin(),
	new HTMLWebpackPlugin({
		filename: './ja/index.html',
		inject: 'head',
		template: 'src/html/ja/index.html',
		chunks: ['index'],
		inlineSource: '.(css)$',
		minify: minifyOption
	}),
	new HTMLWebpackPlugin({
		filename: 'index.html',
		inject: 'head',
		template: 'src/html/index.html',
		chunks: ['index'],
		inlineSource: '.(css)$',
		minify: minifyOption
	}),
	new HTMLWebpackPlugin({
		filename: 'resnet50.html',
		inject: 'head',
		template: 'src/html/resnet50.html',
		chunks: ['resnet50'],
		inlineSource: '.(css)$',
		minify: minifyOption
	}),
	new HTMLWebpackPlugin({
		filename: 'neural_style_transfer.html',
		inject: 'head',
		template: 'src/html/neural_style_transfer.html',
		chunks: ['neural_style_transfer'],
		inlineSource: '.(css)$',
		minify: minifyOption
	}),
	new HTMLWebpackPlugin({
		filename: 'resnet50.es5.html',
		inject: 'head',
		template: 'src/html/resnet50.es5.html',
		chunks: ['resnet50'],
		inlineSource: '.(css)$',
		minify: minifyOption
	}),
	new HTMLWebpackPlugin({
		filename: 'neural_style_transfer.es5.html',
		inject: 'head',
		template: 'src/html/neural_style_transfer.es5.html',
		chunks: ['neural_style_transfer'],
		inlineSource: '.(css)$',
		minify: minifyOption
	})
];

if (process.env.DEBUG) {
	plugins = plugins.concat([
		new HTMLWebpackPlugin({
			filename: 'webcam_ts_test.html',
			inject: 'head',
			template: 'src/html/webcam_ts_test.html',
			chunks: ['webcam_ts_test'],
			inlineSource: '.(css)$',
			minify: minifyOption
		})
	]);
}

plugins = plugins.concat([
	new HTMLWebpackInlineSourcePlugin(),
	new ScriptExtHtmlWebpackPlugin({
		defaultAttribute: 'async'
	}),
	new CopyWebpackPlugin([{
		from: './src/static',
		to: './'
	}]),
]);

module.exports = {
	entry: {
		'index': './src/scripts/index.ts',
		'resnet50': './src/scripts/resnet50.ts',
		'neural_style_transfer': './src/scripts/neural_style_transfer.ts',
		'sw': './src/scripts/sw.ts',
		'webcam_ts_test': './src/scripts/webcam_ts_test.ts',
	},
	output: {
		path: path.resolve(__dirname, './build/webdnn'),
		publicPath: process.env.DEBUG ? '' : 'https://mil-tokyo.github.io/webdnn',
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
	plugins: plugins
};