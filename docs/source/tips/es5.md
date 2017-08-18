# EcmaScript5 support
In some cases, you want to support older browser such as IE11, which is the default browser for Windows 7 and 8. To support IE11, the JavaScript code have to be compliant with EcmaScript5. In this document, how to convert the code is described.

## Use webdnn.es5.js and polyfill
In syntax level, `webdnn.js` uses statements like `await`, which is not compatible with EcmaScript5. Instead, you can use `webdnn.es5.js` which does not use such statements. This library can be compiled with `tsc -p tsconfig.es5.js` on `src/descriptor_runner` directory.

In standard library level, `webdnn.js` uses `Promise` and `fetch`. You need to supply these objects by loading polyfill.

In colusion, you need to insert the following statements in the html.

```
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-polyfill/6.23.0/polyfill.min.js"></script>
<script src="https://cdn.polyfill.io/v2/polyfill.min.js?features=fetch&flags=gated"></script>
<script src="../../lib/inflate.min.js"></script>
<script src="../../dist/webdnn.es5.js"></script>
```

## Converting your own code
If your own JavaScript code uses newer statements like `await`, you can also convert it automatically by [babel](https://babeljs.io/).

Install babel

```
npm install babel-cli babel-preset-env babel-preset-es2015 babel-plugin-transform-regenerator
```

Converting your code

```
babel foo.js --out-file foo.es5.js --presets env,es2015 --plugins transform-regenerator
```
