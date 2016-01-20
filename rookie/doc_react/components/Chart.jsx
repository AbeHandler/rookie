"use strict";
/*
The chart
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var c3 = require('c3');

module.exports = React.createClass({

   padDigits: function(number, digits) {
      let n_string = number.toString();
      if (n_string.length == 1){
        n_string = "0" + n_string
      }
      return n_string;
   },

  shouldComponentUpdate: function(nextProps, nextState) {
    console.log(nextProps);
    console.log(nextState);
    let current_start = moment(this.props.yr_start + "-" + this.props.mo_start + "-" + this.props.dy_start, "YYYY-MM-DD");
    let current_end = moment(this.props.yr_end + "-" + this.props.mo_end + "-" + this.props.dy_end, "YYYY-MM-DD");
    if (this.props.f != nextProps.f){
       console.log(1);
       return true;
    } else if (current_end.format("YYYY") != nextProps.yr_end.toString()){
       console.log(2);
       return true;
    } else if (current_start.format("YYYY") != nextProps.yr_start.toString()){
       console.log(3);
       return true;
    } else if (current_end.format("MM") != this.padDigits(nextProps.mo_end)){
       console.log(4);
       console.log(current_end.format("MM"));
       console.log(nextProps.mo_end.toString());
       return true;
    } else if (current_start.format("MM") != this.padDigits(nextProps.mo_start)){
       console.log(5);
       return true;
    } else if (current_end.format("DD") != this.padDigits(nextProps.dy_end)){
       console.log(6);
       return true;
    } else if (current_start.format("DD") != this.padDigits(nextProps.dy_start)){
       console.log(7);
       return true;
    } else {
       console.log(8);
       return false;
    }
  },

  convert_to_c3_land_subtract: function(dt){
    //workaround for https://github.com/masayuki0812/c3/issues/65
    //return moment(dt).format("YYYY-MM-DD");
    return moment(dt).subtract(15, 'days').format("YYYY-MM-DD");
  },

  render: function() {

    let q = this.props.q;
    let c3_start = this.convert_to_c3_land_subtract(this.props.yr_start + "-" + this.props.mo_start + "-" + this.props.dy_start);
    let c3_end = this.convert_to_c3_land_subtract(this.props.yr_end + "-" + this.props.mo_end + "-" + this.props.dy_end);
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