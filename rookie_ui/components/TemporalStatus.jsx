/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Panel = require('react-bootstrap/lib/Panel');
var moment = require('moment');
var _ = require('lodash');

module.exports = React.createClass({


  render: function() {
    
    let d1;
    let d2;
    let status;
    if (moment(this.props.start_selected).isValid() && moment(this.props.end_selected).isValid()){
        d1 = moment(this.props.start_selected).format("MMM DD, YYYY");
        d2 = moment(this.props.end_selected).format("MMM DD, YYYY");
        status = <span>Showing documents from <span style={{fontWeight: "bold"}}>{d1}</span> to <span style={{fontWeight: "bold"}}>{d2}</span></span>
      }else{
        status = "";
      }
    return (
      <Panel>
         {status}
      </Panel>
    )
  }

});