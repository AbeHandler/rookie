/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');

var UI = require('./components/UI.jsx');

var cache = {};

var width = $(document).width() - 50;

var w_h_ratio = 9;  // width % height for sparkline or chart. used to set aspect ratio

ReactDOM.render(
  <UI w_h_ratio={w_h_ratio} first_story_pubdate={first_story_pubdate} last_story_pubdate={last_story_pubdate} facet_datas={facet_datas} total_docs_for_q={total_docs_for_q} corpus={corpus} chart_bins={chart_bins} q_data={q_data} datas={global_facets} width={width} q={query}/>,
  document.getElementById('example')
);
