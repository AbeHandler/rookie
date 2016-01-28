/* jshint node: true */
"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var d3 = require('d3');
global.$ = global.jQuery = require('jquery');

var Axis = require('./components/axis.jsx');

var Demo = React.createClass({

  getInitialState: function() {
    // naming it initialX clearly indicates that the only purpose
    // of the passed down prop is to initialize something internally
    return {x: 100, y: 100};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  handleMouseMove: function(e) {
    this.setState({x: e.pageX, y: e.pageY});
  },

  get_height: function(i, scale){
    return scale(i);
  },

  get_y_offset: function(i, scale){
    let height = this.get_height(i, scale);
    return this.props.height - scale(i);
  },

  handleclick: function(e){
    // console.log(e);
  },

  handleMouseDown: function(e) {
    //console.log(e.pageX);
    //console.log(e.pageY);
  },
  
  handleMouseUp: function(e) {
    //console.log(e.pageX);
    //console.log(e.pageY);
  },

  render: function() {
    let min = _.min(this.props.data);
    let max = _.max(this.props.data);
    let height = this.props.height;
    let width = this.props.width;
    let lateralize = this.lateralize;
    let get_height = this.get_height;
    let get_y_offset = this.get_y_offset;
    let lateral_scale = d3.scale.linear()
                        .domain([-1, this.props.data.length])
                        .range([0, width]);
    let height_scale = d3.scale.linear()
                        .domain([0, max])
                        .range([0, height]);
    let xAxis = d3.svg.axis()
                   .scale(height_scale);
    let cliq = this.handleclick;

    return (

        <div>
        <svg width={this.props.width} height="400">
        <rect onMouseMove={this.handleMouseMove} onMouseDown={this.handleMouseDown} onMouseDown={this.handleMouseDown}  onMouseUp={this.handleMouseUp} y="0" x="0" opacity=".25" height={this.props.height} width={this.props.width} stroke="green" strokeWidth="4" fill="blue" />
        {this.props.data.map(function(object, i){
            return <rect key={i} onClick={e=>cliq(i)} y={get_y_offset(object, height_scale)} x={lateralize(i, lateral_scale)} height={get_height(object, height_scale)} width="14" stroke="green" strokeWidth="4" fill="yellow" />
        })}
        <line x1="0" y1="325" x2={this.props.width} y2="325" stroke="black" strokeWidth="5"/>
        {this.props.data.map(function(object, i){
            return <text key={i} x={lateralize(i, lateral_scale)} y="350" fill="black">{i}</text>
        })}
        <line x1={this.state.x} y1="0" x2={this.state.x} y2="50" stroke="black" strokeWidth="5"/>
        </svg>
        </div>
          
    );
  }
});

ReactDOM.render(
  <Demo height="300" width="900" data={[ 100, 32, 100, 325, 230, 253, 235, 435, 346, 200, 300, 400, 500 ]} />,
  document.getElementById('example')
);