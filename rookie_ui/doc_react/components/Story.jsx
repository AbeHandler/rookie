"use strict";
/*
A result in a normal IR system 
*/

var React = require('react');
var moment = require('moment');

module.exports = React.createClass({

     render: function(){
        var markup = function(doc) { 
            return {__html: doc + "..."};
        };
        let headlineStyle = {
            color: "#323232",
            fontWeight: "bold"
        };
        let snippetStyle = {
            color: "grey",
            fontSize: "small"
        };
        let dateStyle = {
            width: "9%",
            float: "left",
            color: "#778899",
            overflow: "hidden",
            fontSize: "large"
        };
        let storyStyle = {
            width: "91%",
            float: "left"
        };
        let rowStyle = {
            width: "100%",
            borderStyle: '1px solid black'
        };
        let yrStyle = {
            color: "black",
            fontSize: "13"
        };
        let mom = moment(this.props.story.pubdate);
        return (
            <div style={rowStyle}>
                <div style={dateStyle}>
                    <div>{mom.format("MMM DD")}</div>
                    <div style={yrStyle}>{mom.format("YYYY")}</div>
                </div>
                <div style={storyStyle}>
                    <a style={headlineStyle}> <div>{this.props.story.headline}</div> </a>
                    <div style={snippetStyle} dangerouslySetInnerHTML={markup(this.props.story.snippet)}/>
                </div>
            </div>
        );
    }
});
