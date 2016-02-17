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
    
    let chunks = _.chunk(_.keys(this.props.facet_datas), _.keys(this.props.facet_datas).length/this.props.col_no);
    let col_width = this.props.width / this.props.col_no;
    let col_range = _.range(3);
    let facet_datas = this.props.facet_datas;
    let q_data = this.props.q_data;
    let clickTile = this.props.clickTile;
    let w_h_ratio = this.props.w_h_ratio;
    return (
            <Grid>
            {col_range.map(function(value, i){
                   return <Row key={i} className="show-grid">
                   {chunks[value].map(function(k1, v1){
                      return <Col xs={4}>
                              <SparklineTile clickTile={clickTile} key={k1} facet={k1} width={col_width} w_h_ratio={w_h_ratio} q_data={q_data} f_datas={facet_datas[k1]}/>
                              </Col>
                    })}
                   </Row>
                })
              }
            </Grid>
    );
  }
});
