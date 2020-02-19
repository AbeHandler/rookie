'use strict';
/*
Axis.jsx
*/

var React = require('react');
var d3 = require('d3');
var moment = require('moment');

export default class XAxis extends React.Component{

  i_to_date(i){
    if (i % this.props.show_nth_tickmark == 0){
      return moment(this.props.keys[i], "YYYY-M-D").format("MMM YYYY");
    } else{
      return "";
    }
  }

  render() {
    let lateralize = this.props.lateralize;
    let to_date = this.i_to_date;
    let lateral_scale = this.props.lateral_scale;
    let keys = this.props.keys;
    let ticks = lateral_scale.ticks(d3.timeYear);
    let format = lateral_scale.tickFormat();
    let x_label_height = this.props.width/2;
    let y_label_height = this.props.height * .9;
    return (
        <svg height={this.props.height} width={this.props.width}>
        <line key={"sd03"} x1="0" y1="10" x2={this.props.width} y2="10" stroke="black" strokeWidth="3"/>
        {ticks.map(function(object, i){
            return (<g key={i + "gjg"}>       
                   <line key={() => {i + '_lll'}} x1={lateralize(object, lateral_scale)} x2={lateralize(object, lateral_scale)} y1="3" y2="10" stroke="black" strokeWidth="1"/>
                   <text key={() => {i + '_k'}} x={lateralize(object, lateral_scale)} y="25" fill="black">{format(object)}</text>
                   </g>)
        })}
        <text key={"sdsd03"} x={x_label_height} y={y_label_height} fontSize="12px"> Publication date</text>
        </svg>
    );
  }
}
