// Requiring Gulp
var gulp = require('gulp');
var browserify = require('browserify');
var browserSync = require('browser-sync');
var source = require('vinyl-source-stream');
var React = require('react');
var ReactDOM = require('react-dom');
var jshint = require('gulp-jshint');
var mochaPhantomJS = require('gulp-mocha-phantomjs');

var paths = {
  scripts: ['main.js', "components/*"]
};


gulp.task('b', function() {
    return browserify('main.js')
        .transform("babelify", {presets: ["es2015", "react"]})
        .bundle()
        //Pass desired output filename to vinyl-source-stream
        .pipe(source('bundle.js'))
        // Start piping stream to tasks!
        .pipe(gulp.dest('app/js'))
        // Reloading the stream
        .pipe(browserSync.reload({
           stream: true
        }));
});

// Start browserSync server
gulp.task('browserSync', function() {
  browserSync({
    server: {
      baseDir: 'app'
    }
  })
});

gulp.task('test', function () {
    return gulp
    .src('test/runner.html')
    .pipe(mochaPhantomJS());
});

gulp.task('w', ['browserSync'], function() {
  gulp.watch(paths.scripts, ['b']);
});