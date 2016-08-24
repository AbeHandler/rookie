// Requiring Gulp
var gulp = require('gulp');
var browserify = require('browserify');
var browserSync = require('browser-sync');
var source = require('vinyl-source-stream');
var autoprefixer = require('gulp-autoprefixer');
var cssnano = require('gulp-cssnano');
var rename = require('gulp-rename');
var assign = require('lodash.assign');
var gutil = require('gulp-util');
var sourcemaps = require('gulp-sourcemaps');
var React = require('react');
var ReactDOM = require('react-dom');

var debug = require('gulp-debug');
var watchify = require('watchify');

var shell = require('gulp-shell')

var buffer = require('vinyl-buffer');

var paths = {
  scripts: ['components/*','main.js']
};


var customOpts = {
  entries: ['main.js'],
  debug: true,
  verbose:true,
  transform:"babelify"
};

var opts = assign({}, watchify.args, customOpts);
var b = watchify(browserify(opts));

// add transformations here
// i.e. b.transform(coffeeify);

function bundle() {

  gutil.log('Compiling JS...');

  return b.bundle()
    // log errors if they happen
    .on('error', gutil.log.bind(gutil, 'Browserify Error'))
    .pipe(source('bundle.js'))
    .pipe(debug({title: 'js:', minimial: 'false'}))
    // optional, remove if you don't need to buffer file contents
    .pipe(buffer())
    // optional, remove if you dont want sourcemaps
    .pipe(sourcemaps.init({loadMaps: true})) // loads map from browserify file
       // Add transformation tasks to the pipeline here.
    .pipe(sourcemaps.write('.')) // writes .map file
    .pipe(gulp.dest('../webapp/static/js/'))
    .pipe(gulp.dest('../../papers/chi2017/turk/webapp/static/js'));
}

gulp.task('js', bundle); // so you can run `gulp js` to build the file
b.on('update', bundle); // on any dep update, runs the bundler
b.on('log', gutil.log); // output build logs to terminal


gulp.task('script', function() {
  return
    // lint command
    // uglify and minify commands
    gulp.pipe(debug({title: 'script', minimial: 'false'}))
    .pipe(source('../webapp/static/js/bundle.js'))
    .pipe(debug({huh: 'sdasdf'}))
    .pipe(gulp.dest('../../papers/chi2017/turk/webapp/static/js')) // <- Destination to one location
});

gulp.task('hobbes', shell.task([
  './deploy_hobbes.sh'
]))

gulp.task('w', function() {
  gulp.watch(paths.scripts, ['js', 'hobbes']);
});
