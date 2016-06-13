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
            return "document";
        } else{
            return "documents";
        }
    },

    render: function() {

        let text_dec = "none";
        let on_click_f = "";
        if (this.props.mode == "overview"){
            text_dec = "underline";
        }
        let status_start = <span>Found {this.props.ndocs} <span onClick={on_click_f} style={{textDecoration: text_dec}}>{this.getStoryPhrase()}</span> for </span>;
        let f = this.props.f;
        let show = (f != -1 & f != undefined);
        let tot_f_docs = this.props.f_docs;
        if (this.props.f != -1){
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={this.props.q_color} text={this.props.q}/> — <span style={{fontWeight: "bold"}}>{tot_f_docs}</span> mention <ClickableQF showX={true} xHandler={this.props.fX} color={this.props.f_color} text={this.props.f}/> </span>
        } else {
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={this.props.q_color} text={this.props.q}/> <span style={{float: "right"}}></span></span>
        }
    }
});
