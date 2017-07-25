const fs = require('fs');
const path = require('path');
const mkdirp = require('mkdirp');
const hapi = require('hapi');
const inert = require('inert');
const phantom = require('phantomjs-prebuilt');
const childProcess = require('child_process');
const portFinder = require('portfinder');

function compileToHTML(staticDir, route, options, callback) {
	function serveAndPrerenderRoute() {
		portFinder.getPort((err, port) => {
			if (err) throw err;
			
			let server = new hapi.Server({
				connections: {
					routes: {
						files: {
							relativeTo: staticDir
						}
					}
				}
			});
			
			server.connection({ port: port });
			
			server.register(inert, (err) => {
				if (err) throw err;
				
				server.route({
					method: 'GET',
					path: route,
					handler: (request, reply) => reply.file(path.join(staticDir, options.indexPath))
				});
				
				server.route({
					method: 'GET',
					path: '/{param*}',
					handler: {
						directory: {
							path: '.',
							redirectToSlash: true,
							index: true
						}
					}
				});
				
				server.start(err => {
					// If port is already bound, try again with another port
					if (err) return serveAndPrerenderRoute();
					
					let maxAttempts = options.maxAttempts || 5;
					let attemptsSoFar = 0;
					
					let phantomArguments = [
						path.join(__dirname, 'phantom-page-render.js'),
						'http://localhost:' + port + route,
						JSON.stringify(options)
					];
					
					if (options.phantomOptions) {
						phantomArguments.unshift(options.phantomOptions)
					}
					
					function capturePage() {
						attemptsSoFar++;
						
						childProcess.execFile(phantom.path, phantomArguments, { maxBuffer: 1048576 }, (err, stdout, stderr) => {
							if (err || stderr) {
								// Retry if we haven't reached the max number of capture attempts
								if (attemptsSoFar <= maxAttempts) {
									return capturePage()
								} else {
									if (err) throw stdout;
									if (stderr) throw stderr;
								}
							}
							
							callback(stdout);
							server.stop();
						});
					}
					
					capturePage();
				})
			})
		})
	}
	
	serveAndPrerenderRoute();
}

class PrerenderSpaPlugin {
	constructor(staticDir, paths, options) {
		this.staticDir = staticDir;
		this.paths = paths;
		this.options = options || {};
	}
	
	apply(compiler) {
		compiler.plugin('after-emit', (compilation, done) => {
			Promise.all(
				this.paths.map((outputPath) => {
					return new Promise((resolve, reject) => {
						compileToHTML(this.staticDir, outputPath, this.options, (prerenderedHTML) => {
							if (this.options.postProcessHtml) {
								prerenderedHTML = this.options.postProcessHtml({
									html: prerenderedHTML,
									route: outputPath
								});
							}
							
							fs.writeFile(path.join(this.staticDir, outputPath), prerenderedHTML, (err) => {
								if (err) {
									return reject('Could not write file: ' + file + '\n' + error)
								}
								resolve()
							});
						});
					})
						.then(() => done())
						.catch((err) => {
							// setTimeout prevents the Promise from swallowing the throw
							setTimeout(() => {
								throw error
							}, 1);
						});
				})
			);
		});
	}
}

module.exports = PrerenderSpaPlugin;
