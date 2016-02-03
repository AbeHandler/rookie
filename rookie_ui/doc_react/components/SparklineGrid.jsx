'use strict';
/*
SparlineGrid.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');


var SparklineTile = require('./SparklineTile.jsx');
var Sparkline = require('./Sparkline.jsx');

module.exports = React.createClass({

  render: function() {
    
    let sparkline_tile = {
      width: this.props.width,
      height: this.props.tileheight
    }
    
    //let datas_range = _.range(0, _.keys(this.props.facet_datas).length, 1);
    let chunks = _.chunk(_.keys(this.props.facet_datas), _.keys(this.props.facet_datas).length/this.props.col_no);
    let l_col = {
      width: "33%",
      float: "left",
      borderLeftColor: "grey",
      borderLeftWidth: "1",
      borderLeftStyle: "solid"
    }
    let l_col_no_border = {
      width: "33%",
      float: "left"
    }
    let full = {
      width: "100%"
    }
    let col_width = this.props.width / this.props.col_no;
    let col_range = _.range(3);
    let facet_datas = this.props.facet_datas;
    let q_data = this.props.q_data;
    let clickTile = this.props.clickTile;
    return (
          <div style={full}>
            {col_range.map(function(value, i){
                   return <div style={i == 0 ? l_col_no_border : l_col} key={i}>
                   {chunks[value].map(function(k1, v1){
                      return <SparklineTile clickTile={clickTile} key={k1} facet={k1} width={col_width} height="45" q_data={q_data} f_datas={facet_datas[k1]}/>
                    })}
                   </div>
                })
              }
          </div>
    );
  }
});
