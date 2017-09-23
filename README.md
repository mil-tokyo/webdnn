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