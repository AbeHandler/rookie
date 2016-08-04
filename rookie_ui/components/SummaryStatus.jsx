/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Panel = require('react-bootstrap/lib/Panel');
var moment = require('moment');
var _ = require('lodash');
var ClickableQF = require('./ClickableQF.jsx');


module.exports = React.createClass({

  resetT: function(){
    this.props.resetT();
  },

  render: function() {

    let status;
    let summary_of = "";
    let summary_toggle = "";
    let inc_x = "";
    if (this.props.show_x){
      inc_x = <sup onClick={this.resetT}
                    style={{cursor: "pointer", fontWeight: "bold"}}>X</sup>;
    }
    if (this.props.kind_of_doc_list == "summary_baseline"){
      summary_of = "Summary of ";
    }else{
      summary_of = "Showing ";
      summary_toggle = <span onClick={()=>this.props.turnOnSummary()} style={{float: "right", textDecoration: "underline", cursor: "pointer"}}>summarize</span>
    }
    if (moment(this.props.start_selected).isValid() && moment(this.props.end_selected).isValid()){
        let d1 = moment(this.props.start_selected).format("MMM DD, YYYY");
        let d2 = moment(this.props.end_selected).format("MMM DD, YYYY");
        var f_stuff = "";
        if (this.props.f != -1){
          f_stuff = <span>mentioning <span style={{color: this.props.f_color, fontWeight: "bold"}}> {this.props.f} </span> </span>;
        }
        status = <span>
                  <span>{summary_of}{this.props.ndocs} </span>
                  <span><span style={{textDecoration: "underline"}} onClick={()=>this.props.turnOnDoclist()}>documents</span></span>
                  <span> for <span style={{color: this.props.q_color, fontWeight: "bold"}}>
                              {this.props.q}&nbsp;
                            </span>
                  </span>
                  {f_stuff}
                   from <span style={{fontWeight: "bold"}}>{d1}</span>
                  <span style={{fontWeight: "bold"}}> &mdash; {d2}</span>
                  {inc_x}{summary_toggle}
                </span>
      }else{
        status = "";
      }
    return (
      <div>
         {status}
      </div>
    )
  }

});
