'use strict';
/*
SparlineTile.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

var Sparkline = require('./Sparkline.jsx');

var ReactDOM = require('react-dom');

module.exports = React.createClass({

  componentDidMount: function () {
     var width = ReactDOM.findDOMNode(this).offsetWidth /2;
     this.setState({w: width});
  },

  getInitialState: function() {
    return {w: 0};
  },

  handleClick: function(){
    this.props.clickTile(this.props.facet);
  },

  render: function() {

    let width = this.props.width/2;
    let tile_height = width/this.props.w_h_ratio * 3;
    let height = width/this.props.w_h_ratio;
    
    let facet_title_style = {
      paddingTop: "10%",
      paddingLeft: "10%",
      color:"#621b14",
      textOverflow:"clip",
      whiteSpace: "nowrap",
      fontWeight: "bold"
    }
    if (this.props.col_no != 0){
      facet_title_style.borderLeft = "1px solid grey";
    }
    
    let w = this.state.w;
    let h = w / this.props.w_h_ratio;
    return (
          <div onClick={this.handleClick} style={{width: this.props.width, height: tile_height}}>
            <div style={{width: "50%", float: "left"}}>
            <div style={facet_title_style}>{this.props.facet}</div>
            </div>
            <div style={{width: "50%", float: "left", paddingTop: "5%", paddingRight: "5%"}}>
            <Sparkline q_data={this.props.q_data} f_data={this.props.f_datas} width={w} height={h}/>
            </div>
          </div>
    );
  }
});
