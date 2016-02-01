'use strict';
/*
Axis.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');
var moment = require('moment');

module.exports = React.createClass({
  
  shouldComponentUpdate: function(nextProps, nextState){
     if(_.isEqual(nextProps.q, this.props.q)){
      return false;
     }else{
      return true;
     }
  },

  i_to_date: function(i){
    if (i % this.props.show_nth_tickmark == 0){
      return moment(this.props.keys[i], "YYYY-M-D").format("MMM YYYY");
    } else{
      return "";
    }
  },

  render: function() {
    let lateralize = this.props.lateralize;
    let to_date = this.i_to_date;
    let lateral_scale = this.props.lateral_scale;
    return (
        <svg height={this.props.height} width={this.props.width}>
        <line x1="0" y1="10" x2={this.props.width} y2="10" stroke="black" strokeWidth="3"/>
        {this.props.q_counts.map(function(object, i){
            return <text key={i} x={lateralize(i, lateral_scale)} y="25" fill="black">{to_date(i)}</text>
        })}
        </svg>
    );
  }
});