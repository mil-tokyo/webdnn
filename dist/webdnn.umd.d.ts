/// <reference path="./webdnn.d.ts" />

/**
 * If you want to use "webdnn.js" from typescript, refer this dts file as follows:
 *
 *    ///<reference path="./dist/webdnn.umd.d.ts">
 *
 * However It's highly recommended to bundle your source code with unbundled webdnn source files.
 * You can get these files via npm.
 */

export * from "webdnn/webdnn";
export as namespace WebDNN;
