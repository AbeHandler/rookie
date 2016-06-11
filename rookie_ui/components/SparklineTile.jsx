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
    if (this.props.col_no != 0){
      facet_title_style.borderLeft = "1px solid grey";
    }
    let bc = "white";
    if (this.props.selected){
      bc = "rgba(100,100,100,0.2)";
    }
    let w = (this.props.width - 50)/2;
    let spark_h = w/this.props.w_h_ratio;
    return (
          <div style={{border:"1px solid blue",
                      width:"100%",
                      height:this.props.height}}
                      onClick={this.handleClick}>
              <div style={{border:"1px solid green",
                          width:w,
                          height:this.props.height,
                          color:"#621b14",
                          fontWeight: "bold",
                          cursor: "pointer",
                          float: "left"}}>
                          {this.props.facet}
              </div>
              <div style={{border:"1px solid black",
                          width: w,
                          height:this.props.height,
                          float: "right"}}>

                <Sparkline  q_data={this.props.q_data}
                            f_data={this.props.f_datas}
                            width={w}
                            height={spark_h}/>
              </div>
          </div>
    );
  }
});
