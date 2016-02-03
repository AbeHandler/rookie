'use strict';
/*
SparlineTile.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

var Axis = require('./Axis.jsx');
var Bar = require('./Bar.jsx');
var Sparkline = require('./Sparkline.jsx');

module.exports = React.createClass({


  handleClick: function(){
    this.props.clickTile(this.props.facet);
  },

  render: function() {
    let l_style = {
      width: "50%",
      float:"left",
      paddingRight: "5%"
    }
    let big_w = {
      width: this.props.width,
      height: this.props.height
    }
    let facet_title_style = {
      paddingTop: "10%",
      paddingLeft: "10%",
      color:"#621b14"
    }
    return (
          <div onClick={this.handleClick} style={big_w}>
            <div style={l_style}>
            <div style={facet_title_style}>{this.props.facet}</div>
            </div>
            <div style={l_style}>
            <Sparkline q_data={this.props.q_data} f_data={this.props.f_datas} width={this.props.width/2.5} height="50"/>
            </div>
          </div>
    );
  }
});
