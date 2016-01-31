'use strict';
/*
Bar.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

module.exports = React.createClass({
  
  shouldComponentUpdate: function(nextProps, nextState){
     if(_.isEqual(nextProps.q, this.props.q) & _.isEqual(nextProps.f, this.props.f)){
      return false;
     }else{
      return true;
     }
  },

  render: function() {
    let keystring=this.props.i + this.props.type;
    return (
        <rect key={keystring} onMouseMove={e=> this.props.set_X(this.props.lateral_scale(Math.floor(this.props.lateral_scale.invert(e.pageX))))} onMouseUp={this.props.drag_stop} onClick={e=>cliq(this.props.i)} y={this.props.get_y_offset(this.props.value, this.props.height_scale)} x={this.props.lateralize(this.props.i, this.props.lateral_scale)} height={this.props.get_height(this.props.value, this.props.height_scale)} width="14" strokeWidth="0" fill={this.props.color} opacity=".25" />
    );
  }
});