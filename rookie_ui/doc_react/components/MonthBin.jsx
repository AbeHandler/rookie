/* jshint node: true */
"use strict";
var React = require('react');

module.exports = React.createClass({
    
    handleClick: function(n){
        this.props.monthClick(n);
    },

    render: function(){
        let dStyle = {
            "color":"black"
        };
        if (this.props.selected_mo){
            dStyle.opacity="1";
            dStyle.backgroundColor = "rgba(102,126,199,.1)"; //same as region color
        }else{
            dStyle.opacity=".4";
            dStyle.color="grey";
        }
        return <div style={dStyle} onClick={this.handleClick.bind(this, this.props.monthNo)}>{this.props.month}</div>;
    }
});
