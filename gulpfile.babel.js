import gulp from 'gulp';
import sass from 'gulp-sass';
import {exec} from 'child_process';

function style() {
    return gulp.src('./docs/template/typedoc/style/style.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('./docs/template/typedoc/assets/css'));
}

function doc(callback) {
    exec('yarn run build-doc-ts', (err, stdout, stderr) => {
        if (stdout) console.log(stdout);
        if (stderr) console.error(stderr);
        if (err) console.error(err);
        callback(err);
    });
}

function watch() {
    gulp.watch('./docs/template/typedoc/style/**/*.scss', gulp.series(style, doc));
    gulp.watch('./docs/template/typedoc/layouts/**/**', doc);
    gulp.watch('./docs/template/typedoc/partials/**/**', doc);
    gulp.watch('./docs/template/typedoc/templates/**/**', doc);
    gulp.watch('./src/descriptor_runner/**/*.ts', doc);
    gulp.watch('./src/descriptor_runner/**/*.md', doc);
}

export default gulp.series(style, doc, watch);
