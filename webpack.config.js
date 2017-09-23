const path = require('path');
const { CheckerPlugin } = require('awesome-typescript-loader');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const webpack = require('webpack');

function generateConfig(tsxPath) {
	let chunkName = path.basename(tsxPath, '.tsx');
	return {
		entry: {
			[chunkName]: tsxPath
		},
		output: {
			path: path.resolve(__dirname, './build/webdnn', path.dirname(chunkName)),
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
				use: [
					{ loader: 'style-loader' },
					{
						loader: 'typings-for-css-modules-loader',
						options: {
							modules: true,
							camelCase: true,
							namedExport: true,
							minimize: false,
						}
					},
					{ loader: 'postcss-loader' },
					{ loader: 'sass-loader' }]
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
		plugins: [
			new webpack.DefinePlugin({
				'process.env': {
					NODE_ENV: JSON.stringify('production')
				}
			}),
			new CheckerPlugin(),
			CopyWebpackPlugin([{
				from: './src/static',
				to: './'
			}])
		],
		externals: {
			'webdnn': 'WebDNN'
		}
	};
}


// noinspection WebpackConfigHighlighting
module.exports = [
	generateConfig('./src/scripts/index/index.tsx'),
	generateConfig('./src/scripts/index/index_ja.tsx'),
	generateConfig('./src/scripts/neural_style_transfer/neural_style_transfer.tsx'),
	generateConfig('./src/scripts/resnet50/resnet50.tsx'),
	generateConfig('./src/scripts/yolo9000/yolo9000.tsx')
];