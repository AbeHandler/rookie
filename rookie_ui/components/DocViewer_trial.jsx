"use strict";
/*
Doc viewer
*/

var React = require('react');
var Story = require('./Story.jsx');
var _ = require('lodash');
var moment = require('moment');
var Panel = require('react-bootstrap/lib/Panel');

module.exports = React.createClass({

    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return {__html: dt + " | " + doc.snippet.htext};
    },

    get_docs_to_render: function(){
        let docs = _.filter(this.props.docs, function(d) { 
            return moment(d.pubdate) > moment(this.props.start_selected, "YYYY-MM-DD") && 
                   moment(d.pubdate) < moment(this.props.end_selected, "YYYY-MM-DD")
        }, this);
        docs = _.sortBy(docs, function(d){
            return moment(d.pubdate);
        });
        console.log("asdfasdfasdf".visualLength());
        return docs;
    },

    render: function(){
        
        let docs = this.get_docs_to_render();
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
        console.log(this.props.height);
        return(
            <Panel style={{backgroundColor: "green", height: this.props.height, overflow: "hidden"}}>
                {docs.map(function(doc, n) {
                    return <div key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/>;
                })}
           </Panel>
        );
       }
});
