"use strict";
/*
Name
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
         var divStyle = {
            "paddingRight": "5px",
            "paddingLeft": "5px",
            "marginLeft": "3px",
            "marginRight": "3px",
            "fontWeight": "bold",
            "backgroundColor": "#D3D3D3",
            "color": "black",
            "fontSize":12
         };
         if (this.props.selected){
            divStyle.color = "rgb(0, 40, 163)";
         }
         if (this.props.hovered){
            divStyle.color = "#b33125";
         }
         return (<div onMouseLeave={this.handleHoverOut.bind(this, this.props.name)} onMouseEnter={this.handleHoverIn.bind(this, this.props.name)} className="button tiny secondary" style={divStyle} name={this.props.name} onClick={this.handleClick.bind(this, this.props.name)}>
            {this.props.name}
        </div>);
    }
});