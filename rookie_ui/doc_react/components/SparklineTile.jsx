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

  render: function() {
    let l_style = {
      width: "50%",
      float:"left"
    }
    let big_w = {
      width: this.props.width,
      height: this.props.height
    }
    let facet_title_style = {
      paddingTop: "10%"
    }
    return (
          <div style={big_w}>
            <div style={l_style}>
            <div style={facet_title_style}>{this.props.facet}</div>
            </div>
            <div style={l_style}>
            <Sparkline width={this.props.width/2} height="50" datas={this.props.datas}/>
            </div>
          </div>
    );
  }
});
