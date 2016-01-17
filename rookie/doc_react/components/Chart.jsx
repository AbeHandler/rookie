"use strict";
/*
A chart
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var c3 = require('c3');

module.exports = React.createClass({

  render: function() {

    let q = this.props.q;
    let q_data = this.props.q;
    let chart_bins = this.props.chart_bins;
    let vars = this.props.vars;
    console.log(vars);

    let reg;
    if (this.props.yr_start != -1){
        reg = [{axis: 'x', start: this.props.yr_start + "-" + this.props.mo_start + "-" + this.props.dy_start, end: this.props.yr_end + "-" + this.props.mo_end + "-" + this.props.dy_end, class: 'regionX'}];
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
         width: 1
        },
        types: types
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
