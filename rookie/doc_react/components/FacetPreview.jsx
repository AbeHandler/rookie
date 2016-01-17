"use strict";
/*

*/

var React = require('react');

module.exports = React.createClass({
    handleClick: function(e) {
        this.props.onClick(e);
    },
    render: function() {
         let tmp = this.props.color;
         var aStyle = {
            "color":"grey",
            "fontSize": "small",
            "textDecoration": "underline"
         };
         var spanStyle = {
            "marginRight": "3px"
         };
         let display = this.props.name;
         if (this.props.position + 1 == this.props.len_items){
            return (<span style={spanStyle} name={this.props.name} onClick={this.handleClick.bind(this, this.props.name)}><a style={aStyle}>{display}</a></span>);
         }else{
            return (<span style={spanStyle} name={this.props.name} onClick={this.handleClick.bind(this, this.props.name)}><a style={aStyle}>{display}</a>, </span>);
         }
         
    }
});