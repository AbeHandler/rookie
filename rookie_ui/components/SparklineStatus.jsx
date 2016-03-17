"use strict";
/*
Status message showing q,f,t
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

var ClickableQF = require('./ClickableQF.jsx');

module.exports = React.createClass({


    getStatusStart: function (){
        return "Subjects related to ";
    },

    render: function() {

        let status_start = this.getStatusStart();

        let q_color = "#0028a3";
        let f_color = "#b33125";
        let f = this.props.f;
        let show = (f != -1 & f != undefined);
            return <span><span>{status_start}</span> <ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/>: </span>
    }
});
