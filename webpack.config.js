const path = require('path');
const { CheckerPlugin } = require('awesome-typescript-loader');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HTMLWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const PrerenderSpaPlugin = require('./libs/prerender-spa-plugin');
const webpack = require('webpack');

const DEBUG = process.env.DEBUG;

const hashMap = new Map();

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

function generateConfig(tsxPath, ejsPath, outputName) {
	let chunkName = path.basename(tsxPath, '.tsx');
	
	let entry = {};
	entry[chunkName] = tsxPath;
	
	return {
		entry: entry,
		output: {
			path: path.resolve(__dirname, './build/webdnn', path.dirname(outputName)),
			filename: '[name].js'
		},
		module: {
			rules: [{
				test: /\.tsx?$/,
				use: [{ loader: 'awesome-typescript-loader' }]
			}, {
				test: /\.svg$/,
				use: [{ loader: 'svg-react-loader' }]
			}, {
				test: /\.scss$/,
				use: ExtractTextPlugin.extract({
					fallback: 'style-loader',
					use: [{
						loader: 'typings-for-css-modules-loader',
						options: {
							modules: true,
							camelCase: true,
							namedExport: true,
							minimize: false,
							getLocalIdent: DEBUG ?
								(context, localIdentName, localName, options) => {
									if (!hashMap.has(context.resource)) hashMap.set(context.resource, hashMap.size.toString());
									
									return 'c' + hashMap.get(context.resource) + '_' + localName
								} :
								(context, localIdentName, localName, options) => {
									if (!hashMap.has(context.resource)) hashMap.set(context.resource, hashMap.size.toString());
									if (!hashMap.has(localName)) hashMap.set(localName, hashMap.size.toString());
									
									return 'c' + hashMap.get(context.resource) + '_' + hashMap.get(localName);
								}
						}
					},
						{ loader: 'postcss-loader' },
						{ loader: 'sass-loader' }
					]
				})
			}, {
				test: /\.(png|jpg|json)$/,
				use: [{
					loader: 'file-loader',
					query: {
						name: '[name].[ext]'
					}
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
			DEBUG ? null : new webpack.DefinePlugin({
				'process.env': {
					NODE_ENV: JSON.stringify('production')
				}
			}),
			new ExtractTextPlugin({
				filename: getPath => getPath('[name].css'),
				allChunks: true
			}),
			new CheckerPlugin(),
			DEBUG ? null : new webpack.optimize.UglifyJsPlugin(),
			new HTMLWebpackPlugin({
				filename: path.basename(outputName) + '.html',
				inject: 'head',
				chunksSortMode: 'dependency',
				template: ejsPath,
				minify: DEBUG ? null : minifyOption
			}),
			new PrerenderSpaPlugin(
				path.join(__dirname, './build/webdnn'),
				['/' + outputName + '.html'],
				{
					indexPath: outputName + '.html',
					ignoreJSErrors: true
				}
			),
			CopyWebpackPlugin([{
				from: './src/static',
				to: './'
			}])
		]).filter(v => !!v),
		externals: {
			'webdnn': 'WebDNN'
		}
	};
}


module.exports = [
	generateConfig('./src/scripts/index_ja.tsx', './src/html/index.ejs', 'ja/index'),
	generateConfig('./src/scripts/index.tsx', './src/html/index.ejs', 'index'),
	generateConfig('./src/scripts/neural_style_transfer.tsx', './src/html/app.ejs', 'neural_style_transfer'),
	generateConfig('./src/scripts/resnet.tsx', './src/html/app.ejs', 'resnet')
];