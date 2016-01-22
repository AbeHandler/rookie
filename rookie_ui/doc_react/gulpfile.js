// Requiring Gulp
var gulp = require('gulp');
var browserify = require('browserify');
var browserSync = require('browser-sync');
var source = require('vinyl-source-stream');
var sass = require('gulp-ruby-sass');
var autoprefixer = require('gulp-autoprefixer');
var cssnano = require('gulp-cssnano');
var rename = require('gulp-rename');
var sourcemaps = require('gulp-sourcemaps');
var React = require('react');
var ReactDOM = require('react-dom');
var Sparklines = require('react-sparklines').Sparklines;
var SparklinesLine = require('react-sparklines').SparklinesLine;
var SparklinesSpots = require('react-sparklines').SparklinesSpots;

var paths = {
  scripts: ['components/*','main.js']
};

gulp.task('css', function() {
  return gulp.src('css/*')
    .pipe(sourcemaps.init())
    .pipe(rename({suffix: '.min'}))
    .pipe(cssnano())
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('app/css'))
    .pipe(gulp.dest('../../experiment/static/css'));
});

gulp.task('sass', function() {
  return sass('sass', { style: 'expanded' })
    .pipe(rename({suffix: '.min'}))
    .pipe(cssnano())
    .pipe(gulp.dest('app/css'))
    .pipe(gulp.dest('../../experiment/static/css'));
});

gulp.task('b', ['css', 'sass'], function() {
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