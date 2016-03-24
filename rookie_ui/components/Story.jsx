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
        let dateStyle = {
            width: "9%",
            float: "left",
            color: "#778899",
            overflow: "hidden",
            fontSize: "large"
        };
        let yrStyle = {
            color: "black",
            fontSize: "13"
        };
        let mom = moment(this.props.pubdate);
        console.log(this.props);
        return (
            <div style={{width: "100%", borderStyle: "1px solid black"}}>
                <div style={dateStyle}>
                    <div>{mom.format("MMM DD")}</div>
                    <div style={yrStyle}>{mom.format("YYYY")}</div>
                </div>
                <div style={{width: "91%", float: "left"}}>
                    <a href={this.props.url} target="_blank">
                    <div style={{color: "grey", fontSize: "small"}} dangerouslySetInnerHTML={markup(this.props.snippet)}/>
                    </a>
                </div>
            </div>
        );
    }
});
