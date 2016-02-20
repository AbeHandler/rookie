// Requiring Gulp
var gulp = require('gulp');
var browserify = require('browserify');
var browserSync = require('browser-sync');
var source = require('vinyl-source-stream');
var sass = require('gulp-ruby-sass');
var autoprefixer = require('gulp-autoprefixer');
var cssnano = require('gulp-cssnano');
var rename = require('gulp-rename');
var assign = require('lodash.assign');
var gutil = require('gulp-util');
var sourcemaps = require('gulp-sourcemaps');
var React = require('react');
var ReactDOM = require('react-dom');

var watchify = require('watchify');
var selenium = require('selenium-standalone');

var seleniumServer; // ref for killing selenium server

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
    // optional, remove if you don't need to buffer file contents
    .pipe(buffer())
    // optional, remove if you dont want sourcemaps
    .pipe(sourcemaps.init({loadMaps: true})) // loads map from browserify file
       // Add transformation tasks to the pipeline here.
    .pipe(sourcemaps.write('.')) // writes .map file
    .pipe(gulp.dest('../webapp/static/js/'));
}

gulp.task('js', bundle); // so you can run `gulp js` to build the file
b.on('update', bundle); // on any dep update, runs the bundler
b.on('log', gutil.log); // output build logs to terminal

gulp.task('css', function() {
  return gulp.src(['css/*'])
    .pipe(sourcemaps.init())
    .pipe(rename({suffix: '.min'}))
    .pipe(cssnano())
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('app/css'))
    .pipe(gulp.dest('../webapp/static/css'));
});

gulp.task('sass', function() {
  return sass('sass', { style: 'expanded' })
    .pipe(rename({suffix: '.min'}))
    .pipe(cssnano())
    .pipe(gulp.dest('app/css'))
    .pipe(gulp.dest('../webapp/static/css'));
});

gulp.task('b', ['css', 'sass'], function() {
    return browserify('main.js')
        .transform("babelify", {presets: ["react"]})
        .bundle()
        //Pass desired output filename to vinyl-source-stream
        .pipe(source('bundle.js'))
        // Start piping stream to tasks!
        .pipe(gulp.dest('app/js'))
        .pipe(gulp.dest('../webapp/static/js'))
        // Reloading the stream
        .pipe(browserSync.reload({
           stream: true
        }));
});



var webdriver = require('gulp-webdriver');


gulp.task('e2e', ['selenium'], function() {
  return gulp.src('wdio.conf.js')
    .pipe(webdriver());
});

gulp.task('selenium', function(done) {
  selenium.install({logger: console.log}, function(){
    selenium.start(function(err, child){
      if (err) { 
        console.log("eleeee");
        return done(err);
      }
      seleniumServer = child;
      done();
    });
  });
});

gulp.task('test', ['e2e'], function(){
  seleniumServer.kill();
});


// Start browserSync server
gulp.task('browserSync', function() {
  browserSync({
    server: {
      baseDir: 'app'
    }
  })
})

gulp.task('w', function() {
  gulp.watch(paths.scripts, ['js']);
});