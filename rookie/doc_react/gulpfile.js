// Requiring Gulp
var gulp = require('gulp');
var browserify = require('browserify');
var browserSync = require('browser-sync');
var source = require('vinyl-source-stream');
var React = require('react');
var ReactDOM = require('react-dom');
var Sparklines = require('react-sparklines').Sparklines;
var SparklinesLine = require('react-sparklines').SparklinesLine;
var SparklinesSpots = require('react-sparklines').SparklinesSpots;

var paths = {
  scripts: ['main.js']
};


gulp.task('b', function() {
    return browserify('main.js')
        .transform("babelify", {presets: ["react"]})
        .bundle()
        //Pass desired output filename to vinyl-source-stream
        .pipe(source('bundle.js'))
        // Start piping stream to tasks!
        .pipe(gulp.dest('app/js'))
        .pipe(gulp.dest('../../experiment/static/js'))
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
})

gulp.task('w', ['browserSync'], function() {
  gulp.watch(paths.scripts, ['b']);
});