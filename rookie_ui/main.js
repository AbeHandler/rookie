/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');

var UI = require('./components/UI.jsx');

var cache = {};
var w_h_ratio = 15;  // width % height for sparkline or chart. used to set aspect ratio


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
                datas={global_facets}
                q={query}/>
              }
});
const About = React.createClass({
    render() {
              return <div>app</div>
              }
});
const NoMatch = React.createClass({
    render() {
              return <div>app</div>
              }
});


const routes = (
  <Route path="/" component={App}>
    <Route path="about" component={About} />
    <Route path="*" component={NoMatch} />
  </Route>
)

if (f == "-1"){
  f = -1;
}
        /*{ <Router history={browserHistory}>
          { routes }
        </Router> }*/

ReactDOM.render(
  <Router history={browserHistory}>
          { routes }
  </Router>,
  document.getElementById('example')
);
