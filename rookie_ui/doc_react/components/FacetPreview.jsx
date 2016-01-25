"use strict";
/*
Facet preview
*/

var React = require('react');

module.exports = React.createClass({
    handleClick: function(e) {
        this.props.onClick(e);
    },
    handleHoverIn: function(e) {
        this.props.handleHoverIn(e);
    },
    handleHoverOut: function(e) {
        this.props.handleHoverOut(e);
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
         if (this.props.isHovered){
            aStyle.color = "#0028a3";
         }
         let display = this.props.name;
         if (this.props.position + 1 == this.props.len_items){
            return (<span onMouseLeave={this.handleHoverOut.bind(this, this.props.name)} onMouseEnter={this.handleHoverIn.bind(this, this.props.name)} style={spanStyle} name={this.props.name} onClick={this.handleClick.bind(this, this.props.name)}><a style={aStyle}>{display}</a></span>);
         }else{
            return (<span onMouseLeave={this.handleHoverOut.bind(this, this.props.name)} onMouseEnter={this.handleHoverIn.bind(this, this.props.name)} style={spanStyle} name={this.props.name} onClick={this.handleClick.bind(this, this.props.name)}><a style={aStyle}>{display}</a>, </span>);
         }
         
    }
});