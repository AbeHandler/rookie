/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var moment = require('moment');
var c3 = require('c3');
global.$ = global.jQuery = require('jquery');

var LinguisticFacets = require('./components/LinguisticFacets.jsx');
var TemporalFacets = require('./components/TemporalFacets.jsx');
var DocViewer = require('./components/DocViewer.jsx');
var BinnedLinguisticFacets = require('./components/BinnedLinguisticFacets.jsx');
var UI = require('./components/UI.jsx');

ReactDOM.render(
  <UI chart_bins={chart_bins} vars={f_counts} q_data={q_data} datas={g_facets} height={300} q="Mitch Landrieu" binned_facets={binned_facets} all_results={all_results}/>,
  document.getElementById('example')
);
