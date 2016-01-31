/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var d3 = require('d3');
global.$ = global.jQuery = require('jquery');

var Chart = require('./components/Chart.jsx');

var chart_bins = []; //['2006', '2007', '2008', '2009', '2010', '2011','2012', '2013']


_.forEach(_.range(2002, 2012), function(yr) {
   _.forEach(_.range(1, 12), function(mo) {
       chart_bins.push(yr + "-" + mo + "-" + 1);
    });
});


var binned_counts_q = [];

var binned_counts_f = [];

_.forEach(chart_bins, function(value, key) { 
  binned_counts_q.push(Math.floor((Math.random() * 100) + 1));
});

_.forEach(binned_counts_q, function(value, key) { 
  binned_counts_f.push(Math.floor((Math.random() * value) + 1));
});

ReactDOM.render(
  <Chart q="some q" f="some f" show_nth_tickmark="12" belowchart="50" height="300" width="900" keys={chart_bins} q_counts={binned_counts_q} f_counts={binned_counts_f}/>,
  document.getElementById('example')
);