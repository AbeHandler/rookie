'use strict';
/*
SparlineGrid.jsx
*/

var React = require('react');
var ReactDOM = require('react-dom');
var d3 = require('d3');
var _ = require('lodash');
var SparklineTile = require('./SparklineTile.jsx');
var Sparkline = require('./Sparkline.jsx');
var Panel = require('react-bootstrap/lib/Panel');
var Grid = require('react-bootstrap/lib/Grid');
var Row = require('react-bootstrap/lib/Row');
var Col = require('react-bootstrap/lib/Col');

module.exports = React.createClass({


  render: function() {
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
});
