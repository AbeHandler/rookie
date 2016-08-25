"use strict";
/*
Doc viewer
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

module.exports = React.createClass({

    format_d: function(d){
        return moment(d).format("MMM. DD YYYY");
    },

    //need to use this markup thing b/c snippet has html in it
    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        if (this.props.static_mode){
            return {__html: "<span style='color:black;' >" + doc.snippet.htext + "</span>"};
        }
        else{
            return {__html: "<a style='color:black;' href='" + doc.url + "' target='_blank' >" + doc.snippet.htext + "</a>"};
        }
    },

    render: function(){
        let docs = _.filter(this.props.docs, function(d) {
            return moment(d.pubdate) > moment(this.props.start_selected, "YYYY-MM-DD") &&
                   moment(d.pubdate) < moment(this.props.end_selected, "YYYY-MM-DD")
        }, this);

        docs = _.sortBy(docs, function(d){
            return moment(d.pubdate);
        });
        if (docs.length < 1){
            return <div></div>;
        }
        let f = this.props.f;

        let props = this.props;

        let rowStyle = {
            width:"100%",
            overflow:"hidden"
        };
        let markup = this.markup;
        let format_d = this.format_d;
        return(
            <div style={rowStyle}>
                {docs.map(function(doc, n) {
                    return <div><span style={{color: "grey"}}>{format_d(doc.pubdate)} | </span><span key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/></div>;
                })}
           </div>
        );
       }
});
