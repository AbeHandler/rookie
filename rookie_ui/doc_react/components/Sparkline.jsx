/* jshint node: true */
"use strict";
var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

module.exports = React.createClass({

    get_path_string: function(){

        let bottom = this.props.height;
        let x_scale = d3.scale.linear()
                            .domain([0, this.props.datas.length])
                            .range([0, this.props.width]);
        let y_scale = d3.scale.linear()
                            .domain([0, _.max(this.props.datas)])
                            .range([0, this.props.height]);

        let output = "M 0 " + bottom + " ";
        for (let i = 0; i < this.props.datas.length; i++) {
            let diff = this.props.height - parseFloat(y_scale(this.props.datas[i]));
            output = output + " L " + x_scale(i) + " " + diff;
        }
        output = output + "L " + x_scale(this.props.datas.length - 1) + " " + bottom;
        return output; // + "L 5 30 L 10 40 L 15 30 L 20 20 L 25 40 L 25 50 Z";
    },

    render: function(){
        let ps = this.get_path_string();
        return <svg width={this.props.width} height={this.props.height}><path d={ps} fill="grey" opacity=".25" stroke="black"/></svg>;
    }
});
