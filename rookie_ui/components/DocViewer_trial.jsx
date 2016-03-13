"use strict";
/*
Doc viewer _ trial
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var Panel = require('react-bootstrap/lib/Panel');

module.exports = React.createClass({

    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return {__html: dt + " | " + doc.snippet.htext};
    },

    fake_markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return dt + " | " + doc.snippet.htext;
    },

    get_docs_to_render: function(){
        let docs = this.props.docs;
        let counter = 0;
        let render = [];
        let ht = 0;
        if (docs.length > 0){
            let docs = _.filter(this.props.docs, function(d) { 
                return moment(d.pubdate) > moment(this.props.start_selected, "YYYY-MM-DD") && 
                       moment(d.pubdate) < moment(this.props.end_selected, "YYYY-MM-DD")
            }, this);
            docs = _.sortBy(docs, function(d){
                return moment(d.pubdate);
            });
            let span = moment.duration(moment(this.props.end_selected, "YYYY-MM-DD").diff(moment(this.props.start_selected, "YYYY-MM-DD")));
            let expected = this.props.height / 35; //most are 20 or 40 px tall ish
            let every_n = Math.floor(docs.length / expected);
            let picker = 0;
            while (ht < this.props.height && counter < docs.length){ //pretty hack-y. but apparently this is a weakness in react
                ht += this.fake_markup(docs[picker]).visualHeight();
                if (ht < this.props.height){          
                    render.push(docs[picker]);
                    counter += 1;
                    picker += every_n;
                }
            }   
        }

        //console.log(markup(docs[0]).visualHeight());
        if (render.length > 0){
            return _.sortBy(render, function(d){ return moment(d.pubdate);});
        }else{
            return [];
        }
        
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
        return(
            <Panel style={{backgroundColor: "green", overflowY: "hidden", height: this.props.height, overflow: "hidden"}}>
                {docs.map(function(doc, n) {
                    return <div key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/>;
                })}
           </Panel>
        );
       }
});
