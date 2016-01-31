/*
Chart.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

var Axis = require('./Axis.jsx');
var Bar = require('./Bar.jsx');

module.exports = React.createClass({

  getInitialState: function() {
    // naming it initialX clearly indicates that the only purpose
    // of the passed down prop is to initialize something internally
    return {lscale: -1, x_l: 100, x_r: 700, y_r: 100, drag_l: false, drag_r: false};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  set_X: function(p) {
    if (this.state.drag_l == true & p < this.state.x_r){
      this.setState({x_l: p});
    }
    if (this.state.drag_r == true & p > this.state.x_l){
      this.setState({x_r: p});
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

  get_w: function(l, r){
    return r - l;
  },

  get_key: function(i, r){
    let keystring = i + r;
    return keystring;
  },

  get_bar_width: function(){
    return this.props.width / this.props.q_counts.length;
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
                        .domain([0, this.props.q_counts.length])
                        .range([0, width]);
    let height_scale = d3.scale.linear()
                        .domain([0, max])
                        .range([0, this.props.height]);
    let xAxis = d3.svg.axis()
                   .scale(height_scale);
    let cliq = this.handleclick;
    let drag_stop = this.toggle_drag_stop;
    let set_X = this.set_X;
    let get_key = this.get_key;
    let q = this.props.q;
    let f = this.props.f;
    let bar_width = this.get_bar_width();
    return (

        <div onMouseLeave={this.toggle_drag_stop}>
        <svg width={this.props.width} height={this.props.height}>
        
        {/* background for chart */}
        {/* ->that crazy looking lambda invert scales the X position, takes the floor and then scales it again.
            ->the point of doing that is to limit the possible range of x positions. so x gets mapped to only one of 
            n locations, where n = the number of datapoints. 
          */}
        <rect onMouseMove={e=> set_X(lateral_scale(Math.floor(lateral_scale.invert(e.pageX))))} onMouseUp={this.toggle_drag_stop} y="0" x={this.state.x_l} opacity=".25" height={this.props.height} width={this.get_w(this.state.x_l, this.state.x_r)} strokeWidth="4" fill="grey" />

        {this.props.q_counts.map(function(value, i){
            return <Bar width={bar_width} q={q} f={f} key={get_key("q", i)} color="blue" get_height={get_height} height_scale={height_scale} value={value} i={i} set_X={set_X} lateral_scale={lateral_scale} lateralize={lateralize} drag_stop={drag_stop} get_y_offset={get_y_offset}/>
        })}

        {this.props.f_counts.map(function(value, i){
            return <Bar width={bar_width} q={q} f={f} key={get_key("f", i)} type="f" color="red" get_height={get_height} height_scale={height_scale} value={value} i={i} set_X={set_X} lateral_scale={lateral_scale} lateralize={lateralize} drag_stop={drag_stop} get_y_offset={get_y_offset}/>
        })}
         
        <line onMouseMove={e=> set_X(lateral_scale(Math.floor(lateral_scale.invert(e.pageX))))} onMouseUp={drag_stop} onMouseDown={this.toggle_drag_start} x1={this.state.x_l} y1="0" x2={this.state.x_l} y2={this.props.height} stroke="black" strokeWidth="10"/>
        <line onMouseMove={e=> set_X(lateral_scale(Math.floor(lateral_scale.invert(e.pageX))))} onMouseUp={drag_stop} onMouseDown={this.toggle_drag_start_r} x1={this.state.x_r} y1="0" x2={this.state.x_r} y2={this.props.height} stroke="black" strokeWidth="10"/>
        </svg>
        <Axis show_nth_tickmark="6" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={this.props.width} q_counts={this.props.q_counts} lateralize={lateralize}/>
        </div>
          
    );
  }
});
