const path = require('path');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const { CheckerPlugin } = require('awesome-typescript-loader');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HTMLWebpackPlugin = require('html-webpack-plugin');
const PrerenderSpaPlugin = require('./libs/prerender-spa-plugin');

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

function generateConfig(tsxPath, htmlPath) {
	let chunkName = path.basename(tsxPath, '.tsx');
	
	let entry = {};
	entry[chunkName] = tsxPath;
	
	return {
		entry: entry,
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
				test: /\.svg$/,
				use: [{
					loader: 'svg-react-loader',
				}]
			}, {
				test: /\.scss$/,
				use: ExtractTextPlugin.extract({
					fallback: 'style-loader',
					use: [
						'typings-for-css-modules-loader?module&camelCase&namedExport',
						'postcss-loader',
						'sass-loader'
					]
				})
			}, {
				test: /\.(png|json)$/,
				use: [{
					loader: 'file-loader',
				}]
			}]
		},
		resolve: {
			modules: [
				path.join(__dirname, './src'),
				path.join(__dirname, './node_modules'),
			],
			extensions: ['.ts', '.tsx', '.js', '.jsx', '.scss']
		},
		plugins: ([
			new ExtractTextPlugin({
				filename: getPath => getPath('[name].css'),
				allChunks: true
			}),
			new CheckerPlugin(),
			process.env.DEBUG ? null : new UglifyJSPlugin(),
			new HTMLWebpackPlugin({
				filename: path.basename(htmlPath),
				inject: 'head',
				chunksSortMode: 'dependency',
				template: htmlPath,
				minify: process.env.DEBUG ? null : minifyOption
			}),
			new PrerenderSpaPlugin(
				path.join(__dirname, './build/webdnn'),
				['/' + path.basename(htmlPath)],
				{ indexPath: path.basename(htmlPath) }
			)
		]).filter(v => !!v)
	};
}


module.exports = [
	generateConfig('./src/scripts/index.tsx', './src/html/index.html'),
	generateConfig('./src/scripts/neural_style_transfer.tsx', './src/html/neural_style_transfer.html')
];