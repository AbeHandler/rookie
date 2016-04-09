/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');

var UI = require('./components/UI.jsx');

var cache = {};
var w_h_ratio = 9;  // width % height for sparkline or chart. used to set aspect ratio

ReactDOM.render(
  <UI base_url={base_url} y_axis_width={55} w_h_ratio={w_h_ratio} facet_datas={facet_datas} total_docs_for_q={total_docs_for_q} corpus={corpus} chart_bins={chart_bins} q_data={q_data} datas={global_facets} q={query}/>,
  document.getElementById('example')
);
