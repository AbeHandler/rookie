'use strict';
/*
Axis.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

module.exports = React.createClass({
  
  shouldComponentUpdate: function(nextProps, nextState){
     if(_.isEqual(nextProps.q, this.props.q)){
      return false;
     }else{
      return true;
     }
  },

  render: function() {
    let lateralize = this.props.lateralize;
    let to_date = this.props.to_date;
    let lateral_scale = this.props.lateral_scale;
    return (
        <svg height={this.props.height} width={this.props.width}>
        <line x1="0" y1="10" x2={this.props.width} y2="10" stroke="black" strokeWidth="5"/>
        {this.props.q_counts.map(function(object, i){
            return <text key={i} x={lateralize(i, lateral_scale)} y="25" fill="black">{to_date(i)}</text>
        })}
        </svg>
    );
  }
});