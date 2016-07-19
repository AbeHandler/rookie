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
     var width = ReactDOM.findDOMNode(this).offsetWidth;
     this.setState({w: width});
  },

  getInitialState: function() {
    return {w: 0};
  },

  handleClick: function(){
    this.props.clickTile(this.props.facet);
  },

  render: function() {
    let facet_title_style = {
      paddingTop: "10%",
      paddingLeft: "10%",
      color:"#621b14",
      textOverflow:"clip",
      whiteSpace: "nowrap",
      fontWeight: "bold",
      cursor: "pointer"
    }
    if (this.props.col_no != 0){
      facet_title_style.borderLeft = "1px solid grey";
    }
    let bc = "white";
    if (this.props.selected){
      bc = "rgba(100,100,100,0.2)";
    }
    let w = (this.props.width) - 50;
    let spark_h = this.props.height;
    let spark_w = this.props.w_h_ratio * spark_h;
    return (
          <div style={{
                      width:"100%",
                      backgroundColor:bc,
                      height:this.props.height}}
                      onClick={this.handleClick}>
              <div style={{
                          width:w * .2,
                          height:this.props.height,
                          color:"#621b14",
                          fontWeight: "bold",
                          fontSize: ".8em",
                          cursor: "pointer",
                          float: "left"}}>
                          {this.props.facet}
              </div>
              <div style={{
                          width: w * .8,
                          height:this.props.height,
                          float: "right"}}>

                <Sparkline  q_data={this.props.q_data}
                            f_data={this.props.f_datas}
                            width={spark_w}
                            height={spark_h}/>
              </div>
          </div>
    );
  }
});
