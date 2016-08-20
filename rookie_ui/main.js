/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');

var UI = require('./components/UI.jsx');
var UI_static = require('./components/UI_static.jsx');
var UI_tut = require('./components/UI_tut.jsx');
var Ir = require('./components/Ir.jsx');

var cache = {};
var w_h_ratio = 15;  // width % height for sparkline or chart. used to set aspect ratio


var start = new Date(); 
start = start.toString();

var answers = ["The US government has been a longtime opponent of Bertrand Aristide", 
                "The US government has been a longtime ally of Bertrand Aristide", 
                "The US government was initially an ally of Bertrand Aristide -- but then became an opponent", 
                "The US government was initially an opponent of Bertrand Aristide -- but then became an ally"];

import { Router, Route, Link, browserHistory } from 'react-router' 

const App = React.createClass({
    render() {
                return <UI base_url={base_url}
                y_axis_width={55}
                w_h_ratio={w_h_ratio}
                facet_datas={facet_datas}
                sparkline_per_panel={5}
                total_docs_for_q={total_docs_for_q}
                corpus={corpus}
                f = {f}
                f_counts = {f_counts}
                f_list = {f_list}
                chart_bins={chart_bins}
                q_data={q_data}
                docsperpage={4}
                start = {start}
                datas={global_facets}
                q={query}/>
              }
});
const RookieStatic = React.createClass({
    render() {
                return <UI_static base_url={base_url}
                y_axis_width={55}
                w_h_ratio={w_h_ratio}
                facet_datas={facet_datas}
                sparkline_per_panel={5}
                total_docs_for_q={total_docs_for_q}
                corpus={corpus}
                f = {f}
                answers = {answers}
                start = {start}
                f_counts = {f_counts}
                f_list = {f_list}
                docsperpage={4}
                chart_bins={chart_bins}
                q_data={q_data}
                datas={global_facets}
                q={query}/>
              }
});
const tut = React.createClass({
    render() {
              return <UI_tut base_url={base_url}
                              y_axis_width={55}
                              w_h_ratio={w_h_ratio}
                              facet_datas={facet_datas}
                              sparkline_per_panel={5}
                              total_docs_for_q={total_docs_for_q}
                              corpus={corpus}
                              f = {f}
                              runid = {runid}
                              answers = {answers}
                              f_counts = {f_counts}
                              f_list = {f_list}
                              chart_bins={chart_bins}
                              docsperpage={4}
                              q_data={q_data}
                              start = {start}
                              datas={global_facets}
                              q={query}/>
              }
});
const irmode = React.createClass({
    render() {
              return <Ir base_url={base_url}
                              y_axis_width={55}
                              experiment_mode={true}
                              w_h_ratio={w_h_ratio}
                              facet_datas={facet_datas}
                              sparkline_per_panel={5}
                              total_docs_for_q={total_docs_for_q}
                              corpus={corpus}
                              f = {f}
                              start = {start}
                              sents = {sents}
                              answers = {answers}
                              f_counts = {f_counts}
                              docsperpage={4}
                              f_list = {f_list}
                              chart_bins={chart_bins}
                              q_data={q_data}
                              datas={global_facets}
                              q={query}/>
              }
});
const NoMatch = React.createClass({
    render() {
              return <div>URL not found.</div>
              }
});



if (f == "-1"){
  f = -1;
}

ReactDOM.render(
  <Router history={browserHistory}>
    <Route path="/" component={App}/>
    <Route path="/rookie" component={App}/>
    <Route path="/staticr" component={RookieStatic}/>
    <Route path="/tut" component={tut} />
    <Route path="/ir" component={irmode} />
    <Route path="*" component={NoMatch} />
  </Router>,
  document.getElementById('example')
);
