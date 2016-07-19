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
    let col_range = _.range(this.props.col_no);
    let facet_datas = this.props.facet_datas;
    let q_data = this.props.q_data;
    let clickTile = this.props.clickTile;
    let w_h_ratio = this.props.w_h_ratio;
    let intro = this.props.intro;
    let f = this.props.f;
    let row_range = _.range(this.props.ntile);
    let width = this.props.width;
    let height = this.props.height;
    let ntile = this.props.ntile;
    return (
            <Grid fluid style={{height:height}}>
              {this.props.facet_datas.map(function(value, i){
                     var selected = false;
                     if (f == value["f"]){
                          selected = true;
                     }
                     return  <SparklineTile selected={selected}
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
                  })
                }
            </Grid>
    );
  }
});
