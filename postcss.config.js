module.exports = {
	plugins: [
		require('autoprefixer')({
			browsers: [
				'iOS >= 8'
			]
		}),
		require('postcss-csso')
	]
};