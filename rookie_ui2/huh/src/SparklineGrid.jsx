'use strict';
/*
SparlineGrid.jsx
*/

var React = require('react');
var ReactDOM = require('react-dom');
var d3 = require('d3');
var _ = require('lodash');
import SparklineTile from './SparklineTile.jsx';
import Sparkline from './Sparkline.jsx';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

export default class SparklineGrid extends React.Component{


  render() {
    let col_range = _.range(this.props.col_no);
    let facet_datas = this.props.facet_datas;
    let q_data = this.props.q_data;
    let clickTile = this.props.clickTile;
    let w_h_ratio = this.props.w_h_ratio;
    let intro = this.props.intro;
    let f = this.props.f;
    
    let width = this.props.width;
    let height = this.props.height;

    let displayed = _.filter(this.props.facet_datas, function(o) { 
                                                                  return o.rank >= this.props.startdisplay 
                                                                   && o.rank < this.props.enddisplay }.bind(this));

    let ntile = this.props.enddisplay - this.props.startdisplay;

    if (displayed.length == 0){
      return <div>loading</div>
    }else{
      return (
              <Grid fluid style={{height:height}}>
                {displayed.map(function(value, i){
                       var selected = false;
                       if (f == value["f"]){
                            selected = true;
                       }

                       return  <SparklineTile ref="tile" selected={selected}
                                                 col_no={1}
                                                 clickTile={clickTile}
                                                 key={value["f"]}
                                                 facet={value["f"]}
                                                 width={width}
                                                 height={height/ntile}
                                                 w_h_ratio={w_h_ratio}
                                                 q_data={q_data}
                                                 f_datas={value["counts"]}/>
                })}
              </Grid> 
      );
    }
  }
}
