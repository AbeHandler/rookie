/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var d3 = require('d3');
global.$ = global.jQuery = require('jquery');

var Chart = require('./components/Chart.jsx');

var chart_bins = ['2010-1-1', '2010-2-1', '2010-3-1', '2010-4-1', '2010-5-1', '2010-6-1', '2010-7-1', '2010-8-1', '2010-9-1', '2010-10-1', '2010-11-1', '2010-12-1', '2011-1-1', '2011-2-1', '2011-3-1', '2011-4-1', '2011-5-1', '2011-6-1', '2011-7-1', '2011-8-1', '2011-9-1', '2011-10-1', '2011-11-1', '2011-12-1', '2012-1-1', '2012-2-1', '2012-3-1', '2012-4-1', '2012-5-1', '2012-6-1', '2012-7-1', '2012-8-1', '2012-9-1', '2012-10-1', '2012-11-1', '2012-12-1', '2013-1-1', '2013-2-1', '2013-3-1', '2013-4-1', '2013-5-1', '2013-6-1', '2013-7-1', '2013-8-1', '2013-9-1', '2013-10-1', '2013-11-1', '2013-12-1', '2014-1-1', '2014-2-1', '2014-3-1', '2014-4-1', '2014-5-1', '2014-6-1', '2014-7-1', '2014-8-1', '2014-9-1', '2014-10-1', '2014-11-1', '2014-12-1', '2015-1-1', '2015-2-1', '2015-3-1', '2015-4-1', '2015-5-1', '2015-6-1'];

var binned_counts_q = [];

var binned_counts_f = [];

_.forEach(chart_bins, function(value, key) { 
  binned_counts_q.push(Math.floor((Math.random() * 100) + 1));
});

_.forEach(binned_counts_q, function(value, key) { 
  binned_counts_f.push(Math.floor((Math.random() * value) + 1));
});

ReactDOM.render(
  <Chart q="some q" f="some f" show_nth_tickmark="10" belowchart="50" height="300" width="900" keys={chart_bins} q_counts={binned_counts_q} f_counts={binned_counts_f}/>,
  document.getElementById('example')
);