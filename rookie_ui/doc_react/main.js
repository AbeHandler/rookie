/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var moment = require('moment');
var c3 = require('c3');
global.$ = global.jQuery = require('jquery');

var UI = require('./components/UI.jsx');

var cache = {};

var width = $(document).width() - 50;

ReactDOM.render(
  <UI facet_datas={facet_datas} total_docs_for_q={total_docs_for_q} corpus={corpus} chart_bins={chart_bins} q_data={q_data} datas={global_facets} width={width} q={query} binned_facets={binned_facets} all_results={all_results}/>,
  document.getElementById('example')
);
