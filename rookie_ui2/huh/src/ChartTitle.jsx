"use strict";
/*
Chart title
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

import ClickableQF from "./ClickableQF.jsx"

export default class ChartTitle extends React.Component{

    getStoryPhrase (argument) {
        if ((this.props.ndocs) == 1) {
            return "document";
        } else{
            return "documents";
        }
    }

    render() {
        let status_start = <span>Found {this.props.ndocs} <span>{this.getStoryPhrase()}</span> for </span>;
        let f = this.props.f;
        let show = (f != -1 && f != undefined);
        let show_f = true;
        if (this.props.static_mode){
            show = false;
            show_f = false;
        }
        let tot_f_docs = this.props.f_docs;
        if (this.props.f != -1){
            return <span><span>{status_start}</span><ClickableQF click={this.props.requery} showX={show} xHandler={this.props.qX} color={this.props.q_color} text={this.props.q}/> — <span style={{fontWeight: "bold"}}>{tot_f_docs}</span> mention <ClickableQF click={this.props.fX} showX={show_f} xHandler={this.props.fX} color={this.props.f_color} text={this.props.f}/> </span>
        } else {
            return <span><span>{status_start}</span><ClickableQF click={this.props.requery} showX={show} xHandler={this.props.qX} color={this.props.q_color} text={this.props.q}/> <span style={{float: "right"}}></span></span>
        }
    }
}
