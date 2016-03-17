"use strict";
/*
Doc viewer: generic
*/

var React = require('react');
var DocViewer_baseline = require('./DocViewer_trial.jsx');
var DocViewer = require('./DocViewer.jsx');

module.exports = React.createClass({

    getDocViewer: function(){
        if (this.props.kind_of_doc_list == "summary_baseline"){
            return <DocViewer_baseline {...this.props}/>
        }else{
            return <DocViewer {...this.props}/>
        }
    },
    render: function(){
      return this.getDocViewer();
    }
});
