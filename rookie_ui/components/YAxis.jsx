'use strict';
/*
YAxis.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');
var moment = require('moment');

module.exports = React.createClass({

  render: function() {
    let xp = this.props.y_axis_width / 2;
    console.log(this.props.max);
    console.log(typeof this.props.max);
    let scale = d3.scale.linear().domain(_.range(this.props.max + 1)).range(_.range(this.props.height));
    console.log(scale);
    let ticks = scale.ticks();
    console.log(ticks);
    return (
         <svg width={this.props.y_axis_width} height={this.props.height}>
          <line x1={xp} y1="0" x2={xp} y2={this.props.height} stroke="black" strokeWidth="3" />
	       {ticks.map(function(object, i){                           
            return <text key={i} x="4" y={scale(i)} fill="black">{object}</text>
            })}      
    	  </svg>
	       )
	}
});
