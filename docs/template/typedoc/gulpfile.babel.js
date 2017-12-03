import gulp from 'gulp';
import sass from 'gulp-sass';
import {exec} from 'child_process';

function style() {
    return gulp.src('./style/style.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('./assets/css'));
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
    gulp.watch('./style/**/*.scss', gulp.series(style, doc));
    gulp.watch('./layouts/**/**', doc);
    gulp.watch('./partials/**/**', doc);
    gulp.watch('./templates/**/**', doc);
}

export default gulp.series(style, doc, watch);
