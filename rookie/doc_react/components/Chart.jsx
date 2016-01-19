"use strict";
/*
The chart
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var c3 = require('c3');

module.exports = React.createClass({

  convert_to_c3_land: function(dt){
    //workaround for https://github.com/masayuki0812/c3/issues/65
    return moment(dt).subtract(5, 'days').format("YYYY-MM-DD");
  },

  convert_to_c3_land_add: function(dt){
    //workaround for https://github.com/masayuki0812/c3/issues/65
    return moment(dt).add(5, 'days').format("YYYY-MM-DD");
  },

  render: function() {

    let q = this.props.q;
    let c3_start = this.convert_to_c3_land(this.props.yr_start + "-" + this.props.mo_start + "-" + this.props.dy_start);
    let c3_end = this.convert_to_c3_land_add(this.props.yr_end + "-" + this.props.mo_end + "-" + this.props.dy_end);
    let reg;
    if (this.props.yr_start != -1){
        reg = [{axis: 'x', start: c3_start, end: c3_end, class: 'regionX'}];
    }
    else{
        reg = [];
    }

    let color_array;
    let f = this.props.f;
    let tHandler = this.props.tHandler;
    color_array = {};
    color_array[q] = '#B33125';
    if (this.props.f != -1){
        color_array[f] = '#0028a3';
    }
    let cols;
    let q_data = this.props.q_data;
    let chart_bins = this.props.chart_bins;
    let vars = this.props.vars;
    if (this.props.f == -1){
      cols = [
            q_data,
            chart_bins
        ];
    }else{
      cols = [
            q_data,
            chart_bins,
            vars[f]
        ];
    }
    let types = {};
    types[q] = 'area-spline';
    if (this.props.f != -1){
      types[f] = 'bar';
    }
    let chart = c3.generate({
    size: {
        height: 150
    },
    regions: reg,
    data: {
        x: 'x',
        columns: cols,
        colors: color_array,
        onclick: function (d, e) {
            tHandler(d, e);
            //this.props.tHandler(d, e);
        },
        bar: {
         width: {
            ratio: 0.5 // this makes bar width 50% of length between ticks
          }
        },
        types: types
    },
    point: {
        show: false
    },
     bindto: '#chart',
     axis: {
        x: {
            type: 'timeseries',
            tick: {
                format: function (x) {return moment(x.toString()).format("MMM YYYY");}
            }
        }
    },
    legend: {
        show: false
    },
    tooltip: {
        format: {
            value: function (value, ratio, id, index) {
              return value + " articles"; 
            }
        }
    }
    });
    return <div>
        </div>;
  }
});