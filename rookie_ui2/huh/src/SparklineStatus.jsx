"use strict";
/*
Status message showing q,f,t
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

import ClickableQF from "./ClickableQF.jsx"

export default class SparklineStatus extends React.Component{


    getStatusStart (){
        return "Subjects related to ";
    }

    render() {

        let status_start = this.getStatusStart();

        let q_color = "#0028a3";
        let f_color = "#b33125";
        let f = this.props.f;
        let show = (f != -1 & f != undefined);
        if (this.props.static_mode){
            show = false;
        }
            return <span><span>{status_start}</span> <ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/></span>
    }
}
