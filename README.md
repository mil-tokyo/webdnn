# WebDNN website

## Requirements to build

- Node v6+
- yarn (You can get `npm install -g yarn`)

## How to run

```shell
# setup
$ yarn install

# build
$ yarn run webpack

# run a http server
$ cd ./build
$ python3 -m http.server # or "python2 -m SimpleHTTPServer"
```

# When tagging master branch
Make permanent copy of document

TAG_NAME is like "v1.1.0"
```
cp -R ${WEBDNN}/docs/build/html/ ${WEBDNN_GH}/docs/${TAG_NAME}
```
