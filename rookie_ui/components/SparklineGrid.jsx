'use strict';
/*
SparlineGrid.jsx
*/

var React = require('react');
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
    
    let chunks = _.chunk(_.keys(this.props.facet_datas), this.props.col_no);
    console.log(chunks);
    let col_range = _.range(this.props.col_no);
    let facet_datas = this.props.facet_datas;
    let q_data = this.props.q_data;
    let clickTile = this.props.clickTile;
    let w_h_ratio = this.props.w_h_ratio;
    let cst = this.cst;
    return (
            <Grid fluid>
            {col_range.map(function(value, i){
                   return <Row key={i} style={{height:50}} className="show-grid">
                   {chunks[value].map(function(k1, v1){
                      return <Col xs={4}>
                              <SparklineTile col_no={v1} clickTile={clickTile} key={k1} facet={k1} w_h_ratio={w_h_ratio} q_data={q_data} f_datas={facet_datas[k1]}/>
                              </Col>
                    })}
                   </Row>
                })
              }
            </Grid>
    );
  }
});
