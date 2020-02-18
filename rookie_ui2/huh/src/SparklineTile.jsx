'use strict';
/*
SparlineTile.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

import Sparkline from './Sparkline.jsx';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

var ReactDOM = require('react-dom');

export default class SparklineTile extends React.Component{

  componentDidMount() {
     var width = ReactDOM.findDOMNode(this).offsetWidth;
     this.setState({w: width});
  }

  getInitialState() {
    return {w: 0};
  }

  handleClick(){
    this.props.clickTile(this.props.facet);
  }

  gets(s){
    //console.log(s);
    if (s === true){
      return {color:"#621b14", fontWeight: "bolder", cursor: "pointer", fontSize: ".8em", textDecoration: "underline"}
    }else{
      return {color:"#621b14", fontWeight: "bold", cursor: "pointer", fontSize: ".8em"}
    }
  }

  render() {
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
}
