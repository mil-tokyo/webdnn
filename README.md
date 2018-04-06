# WebDNN Examples

## Requirements to build

- Node v8+
- yarn (You can get by `npm install -g yarn`)

## How to run

```shell
# setup
$ yarn install

# build
# At first time, this command may failed because "Cannot find module './***.scss'".
# In this case please re-run the command.
$ yarn run webpack

# run a http server
$ cd ./build
$ python3 -m http.server # or "python2 -m SimpleHTTPServer"
```

Note that `webdnn.js` does not follow latest version. You have to put latest version of `webdnn.js` and `webdnn.js.map` into `src/static`.

## Deploy
assume current directory is root of `webpage-src` branch, and `../webdnn-gh-pages` is the root of `gh-pages` branch.

```shell
rsync -av --delete build/webdnn/ ../webdnn-gh-pages/ --exclude ".*" --exclude ".*/" --exclude docs
```

