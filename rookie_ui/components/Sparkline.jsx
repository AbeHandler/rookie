/* jshint node: true */
"use strict";
var React = require('react');
var d3 = require('d3');
var _ = require('lodash');


module.exports = React.createClass({

    get_path_string: function(input_data){

        let bottom = this.props.height;
        let x_scale = d3.scale.linear()
                            .domain([0, this.props.q_data.length])
                            .range([0, this.props.width]);
        let y_scale = d3.scale.sqrt()
                            .domain([0, _.max(this.props.q_data)])
                            .range([0, this.props.height]);

        let output = "M 0 " + bottom + " ";
        for (let i = 0; i < input_data.length; i++) {
            let diff = this.props.height - parseFloat(y_scale(input_data[i]));
            output = output + " L " + x_scale(i) + " " + diff;
        }
        output = output + "L " + x_scale(input_data.length - 1) + " " + bottom;
        return output;
    },

    render: function(){
        let q = this.get_path_string(this.props.q_data);
        let f = this.get_path_string(this.props.f_data);
        let fill;
        let indicator = "";
        if (this.props.selected){
            indicator = <rect width={this.props.width} height={this.props.height} fill="grey" opacity=".25"/>
        }else{
            indicator = <path></path>
        }

        return(
            <svg width={this.props.width} height={this.props.height}>
                {indicator}
                <path d={q} fill={"#0028a3"} opacity=".25" stroke="black"/><path d={f} fill="#B33125" opacity=".75" stroke="black"/>
            </svg>
            )
        
    }
});
