/* jshint node: true */
"use strict";
var React = require('react');

module.exports = React.createClass({
    
    handleClick: function(n){
        this.props.handleBinClick(n);
    },
    render: function(){
        let bigStyle = {};
        bigStyle.cursor = "pointer";
        bigStyle.height = this.props.rw_height;
        let bin_key = {textDecoration: "underline", color: "black", fontWeight: "bold"};
        let link = {fontSize: "small", color: "rgb(0, 40, 163)"};
        if (this.props.selected === true){
            bigStyle.backgroundColor = "rgba(153, 153, 153,.1)"; //same as region color
            bigStyle.opacity = 1;
            link.opacity = 1;
        }else{
            link.opacity = .6;
            bigStyle.opacity = .8;
        }
        return <div onClick={this.handleClick.bind(this, this.props.text)} style={bigStyle}><div style={bin_key}>{this.props.text}</div><div style={link}>{this.props.ndocs} stories</div></div>;
    }
});
