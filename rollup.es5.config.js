import typescript from 'rollup-plugin-typescript2'

export default {
    entry: './src/descriptor_runner/webdnn.ts',
    targets: [
        {
            dest: './dist/webdnn.es5.js',
            moduleName: 'WebDNN',
            format: 'umd'
        }
    ],
    sourceMap: true,
    external: [],
    plugins: [
        typescript({
            typescript: require('typescript'),
            tsconfig: './src/descriptor_runner/tsconfig.es5.json'
        })
    ]
}
