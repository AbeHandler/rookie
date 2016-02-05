"use strict";
/*
A Q or and F and a click handler
*/

var React = require('react');

module.exports = React.createClass({

     render: function(){
        let text_style = {
            color: this.props.color,
            "fontWeight": "bold"
        };
        let x_style = {
            color: "black"
        };
        let x_script;
        let x_handler = this.props.xHandler;
        if (this.props.showX){
            x_script = <sup onClick={x_handler} style={x_style}>X</sup>
        }else{
            x_script = ""
        }
        console.log(this.props);
        return (
            <span style={text_style}>
                {this.props.text}{x_script}
            </span>
        );
    }
});
