"use strict";
/*
Doc viewer
*/

var React = require('react');
var Story = require('./Story.jsx');
var _ = require('lodash');
var moment = require('moment');

module.exports = React.createClass({
    
    handleBinDocsZoom: function(e){
        this.props.handleBinDocsZoom(e, this.props.bin_size);
    },

    render: function(){
        let binsize = this.props.bin_size;
        let docs = _.sortBy(this.props.docs, function(d){
            return moment(d.pubdate);
        });
        console.log(docs.length);
        if (docs.length < 1){
            return <div></div>;
        }
        let f = this.props.f;
        var markup = function(doc) { 
           return {__html: doc.snippet};
        };
        let props = this.props;
        var isSelected = function(key, binsize) {
           if (binsize == "year" & props.yr_start.toString() == props.yr_end.toString()){
                if (props.yr_start.toString() == key){
                    return true;
                }
           }
           return false;
        };
        let rowStyle = {
            width:"100%",
            overflow:"hidden"
        };
        return(
            <div style={rowStyle}>
                {docs.map(function(doc, n) {
                    return <div key={n} style={rowStyle}><Story story={doc}/></div>;
                })}
           </div>
        );
       }
});