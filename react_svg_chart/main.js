/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var d3 = require('d3');
global.$ = global.jQuery = require('jquery');

var Axis = require('./components/axis.jsx');

var chart_bins = ['2010-1-1', '2010-2-1', '2010-3-1', '2010-4-1', '2010-5-1', '2010-6-1', '2010-7-1', '2010-8-1', '2010-9-1', '2010-10-1', '2010-11-1', '2010-12-1', '2011-1-1', '2011-2-1', '2011-3-1', '2011-4-1', '2011-5-1', '2011-6-1', '2011-7-1', '2011-8-1', '2011-9-1', '2011-10-1', '2011-11-1', '2011-12-1', '2012-1-1', '2012-2-1', '2012-3-1', '2012-4-1', '2012-5-1', '2012-6-1', '2012-7-1', '2012-8-1', '2012-9-1', '2012-10-1', '2012-11-1', '2012-12-1', '2013-1-1', '2013-2-1', '2013-3-1', '2013-4-1', '2013-5-1', '2013-6-1', '2013-7-1', '2013-8-1', '2013-9-1', '2013-10-1', '2013-11-1', '2013-12-1', '2014-1-1', '2014-2-1', '2014-3-1', '2014-4-1', '2014-5-1', '2014-6-1', '2014-7-1', '2014-8-1', '2014-9-1', '2014-10-1', '2014-11-1', '2014-12-1', '2015-1-1', '2015-2-1', '2015-3-1', '2015-4-1', '2015-5-1', '2015-6-1'];

var binned_counts_q = [];

_.forEach(chart_bins, function(value, key) { 
  binned_counts_q.push(Math.floor((Math.random() * 100) + 1));
});

var Demo = React.createClass({

  getInitialState: function() {
    // naming it initialX clearly indicates that the only purpose
    // of the passed down prop is to initialize something internally
    return {x: 100, y: 100, x_r: 700, y_r: 100, drag_l: false, drag_r: false};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  handleMouseMove: function(e) {
    if (this.state.drag_l == true){
      this.setState({x: e.pageX, y: e.pageY});
    }
    if (this.state.drag_r == true){
      this.setState({x_r: e.pageX, y_r: e.pageY});
    }
  },

  get_height: function(i, scale){
    return scale(i);
  },

  get_y_offset: function(i, scale){
    let height = this.get_height(i, scale);
    return this.props.height - scale(i);
  },

  toggle_drag_start: function(e){
    this.setState({drag_l : true});
  },

  toggle_drag_start_r: function(e){
    this.setState({drag_r : true});
  },

  toggle_drag_stop: function(e){
    this.setState({drag_l : false});
    this.setState({drag_r : false});
  },

  i_to_date: function(i){
    if (i % this.props.show_nth_tickmark == 0){
      return this.props.keys[i];
    } else{
      return "";
    }
    
  },

  render: function() {
    let min = _.min(this.props.q_counts);
    let max = _.max(this.props.q_counts);
    let height = this.props.height;
    let width = this.props.width;
    let lateralize = this.lateralize;
    let get_height = this.get_height;
    let get_y_offset = this.get_y_offset;
    let lateral_scale = d3.scale.linear()
                        .domain([-1, this.props.q_counts.length])
                        .range([0, width]);
    let height_scale = d3.scale.linear()
                        .domain([0, max])
                        .range([0, this.props.height]);
    let xAxis = d3.svg.axis()
                   .scale(height_scale);
    let cliq = this.handleclick;
    let to_date = this.i_to_date;
    let drag_stop = this.toggle_drag_stop;
    return (

        <div>
        <svg width={this.props.width} height={this.props.height}>
        
        {/* background for chart */}
        <rect onMouseMove={this.handleMouseMove} onMouseUp={this.toggle_drag_stop} y="0" x="0" opacity=".25" height={this.props.height} width={this.props.width} strokeWidth="4" fill="grey" />
        {this.props.q_counts.map(function(object, i){
            return <rect onMouseUp={drag_stop} key={i} onClick={e=>cliq(i)} y={get_y_offset(object, height_scale)} x={lateralize(i, lateral_scale)} height={get_height(object, height_scale)} width="14" strokeWidth="4" fill="blue" opacity=".25" />
        })}
         
        <line onMouseUp={drag_stop} onMouseDown={this.toggle_drag_start} x1={this.state.x} y1="0" x2={this.state.x} y2={this.props.height} stroke="black" strokeWidth="10"/>
        <line onMouseUp={drag_stop} onMouseDown={this.toggle_drag_start_r} x1={this.state.x_r} y1="0" x2={this.state.x_r} y2={this.props.height} stroke="black" strokeWidth="10"/>
        </svg>
      {/*  <svg>
        <rect height="100" width="100" fill="blue"/>
        </svg> */}
        <Axis q={this.props.q} to_date={to_date} lateral_scale={lateral_scale} height="50" width={this.props.width} q_counts={this.props.q_counts} lateralize={lateralize}/>
        </div>
          
    );
  }
});

ReactDOM.render(
  <Demo q="some q" show_nth_tickmark="10" belowchart="50" height="300" width="900" keys={chart_bins} q_counts={binned_counts_q} />,
  document.getElementById('example')
);