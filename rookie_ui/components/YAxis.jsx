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
    let yend = this.props.height;
    var scale = d3.scale.ordinal()
	    .domain(_.range(this.props.max))
	    .rangePoints([0, yend]);
    let ticks = _.range(this.props.max);
    let height = this.props.height;
    return (
         <svg width={this.props.y_axis_width} height={this.props.height}>
          <line x1={xp} y1="0" x2={xp} y2={this.props.height} stroke="black" strokeWidth="3" />
	       {ticks.map(function(object, i){                           
            return <text key={i} x="4" y={height - scale(i)} fill="black">{i}</text>
            })}      
    	  </svg>
	       )
	}
});
