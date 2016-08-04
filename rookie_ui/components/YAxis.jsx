'use strict';
/*
YAxis.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');
var moment = require('moment');
var ReactDOM = require('react-dom');

module.exports = React.createClass({

  render: function() {
    let xp = this.props.y_axis_width * .75;
    let yend = this.props.height;
    var scale = d3.scale.linear()
      .domain([0,this.props.max])
      .range([0,yend]);
    let ticks;
    if (this.props.max<7){
  ticks = scale.ticks(this.props.max);
    }else{
        let nticks = Math.floor(this.props.height/22); //fontsize * 2 == 22
  ticks = scale.ticks(Math.floor(this.props.height/(11 * 2))); //_.range(this.props.max);
    }let height = this.props.height;

    let tot = 8;
    let xtot = -1 * (this.props.height * .75);
    return (
         <svg width={this.props.y_axis_width} height={this.props.height}>
          <line ref="yaxis" x1={xp} y1="0" x2={xp} y2={this.props.height} stroke="black" strokeWidth="3" />
         {ticks.map(function(object, i){
            return <text fontSize="11" key={i} x="18" y={yend - scale(object)} fill="black">{object}</text>
            })}
         <text fontSize="11px" x={xtot} y={tot} transform="rotate(270,0,0)"># Stories</text>
         </svg>
         )
  }
});
