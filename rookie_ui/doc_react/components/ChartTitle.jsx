"use strict";
/*
Chart title
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var ClickableQF = require('./ClickableQF.jsx');

module.exports = React.createClass({
  
    getDuration: function(){
        let start = moment(this.props.yr_start + "-" + this.props.mo_start + "-" + this.props.dy_start);
        let end = moment(this.props.yr_end + "-" + this.props.mo_end + "-" + this.props.dy_end);
        var duration = moment.duration(end.diff(start));
        return duration;
    },

    getStoryPhrase: function (argument) {
        if ((this.props.ndocs) == 1) {
            return "story";
        } else{
            return "stories";
        }   
    },

    getTemporalStatus: function (){
        let duration = this.getDuration();
        if (parseInt(this.props.dy_start) === 1 & parseInt(this.props.mo_start) === 1 & this.props.dy_end == "31" & this.props.mo_end == "12"){
            return " in " + this.props.yr_start;
        } else if (Math.floor(duration.asDays()) < 32 & Math.floor(duration.asDays()) > 28){
            let end = moment(this.props.mo_end + "-" + this.props.dy_end + "-" + this.props.yr_end, "MM-DD-YYYY");
            return " in " + end.format("MMM YYYY");
        } else if (Math.floor(duration.asDays()) > 364 & Math.floor(duration.asDays()) < 366){
            return " in " + start.format("YYYY");
        } else {
            return ""; //should not fire
        }
    },

    getStatusWithF: function (){

    },

    getStatusStart: function (){
        return "Found " + this.props.ndocs + " " + this.getStoryPhrase() + " for ";
    },

    render: function() {

        let status_start = this.getStatusStart();
            
        let temporal = this.getTemporalStatus();

        let q_color = "#0028a3";
        let f_color = "#b33125";
        let f = this.props.f;
        let show = (f != -1 & f != undefined);
        if (this.props.f != -1){
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/> and <ClickableQF showX={true} xHandler={this.props.fX} color={f_color} text={this.props.f}/> {temporal} </span>
        } else {
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/> {temporal} </span>
        }
    }
});