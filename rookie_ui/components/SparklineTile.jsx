'use strict';
/*
SparlineTile.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

var Sparkline = require('./Sparkline.jsx');

var Row = require('react-bootstrap/lib/Row');
var Col = require('react-bootstrap/lib/Col');

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

  gets: function(s){
    console.log(s);
    if (s === true){
      return {color:"#621b14", fontWeight: "bolder", cursor: "pointer", fontSize: ".8em", textDecoration: "underline"}
    }else{
      return {color:"#621b14", fontWeight: "bold", cursor: "pointer", fontSize: ".8em"}
    }
  },

  render: function() {
    let w = (this.props.width) - 50;
    let spark_h = w/this.props.w_h_ratio;
    let spark_w = w; // # this.props.w_h_ratio * spark_h;  =  * 
    let gets = this.gets;
    return (
      <Row onClick={this.handleClick} style={{cursor:"pointer"}}>
            <Col xs={12}>
              <div style={gets(this.props.selected)}>
                  {this.props.facet}
              </div>
                <Sparkline  selected={this.props.selected} 
                            q_data={this.props.q_data}
                            f_data={this.props.f_datas}
                            width={spark_w}
                            height={spark_h}/>
            </Col>
        </Row>
    );
  }
});
