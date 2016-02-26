"use strict";
/*
Chart title
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var ClickableQF = require('./ClickableQF.jsx');

module.exports = React.createClass({

    getStoryPhrase: function (argument) {
        if ((this.props.ndocs) == 1) {
            return "story";
        } else{
            return "stories";
        }   
    },
    render: function() {

        let status_start = <span>Found {this.props.ndocs} <span onClick={this.props.turnOnDocMode} style={{textDecoration: "underline"}}>{this.getStoryPhrase()}</span> for </span>;
            

        let q_color = "#0028a3";
        let f_color = "#b33125";
        let f = this.props.f;
        let show = (f != -1 & f != undefined);
        if (this.props.f != -1){
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/> and <ClickableQF showX={true} xHandler={this.props.fX} color={f_color} text={this.props.f}/> </span>
        } else {
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/>  </span>
        }
    }
});
