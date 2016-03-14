"use strict";
/*
Doc viewer _ trial
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var Panel = require('react-bootstrap/lib/Panel');

module.exports = React.createClass({

    shouldComponentUpdate: function(nextProps, nextState) {
          return nextProps.start_selected !== this.props.start_selected &&
                 nextProps.end_selected !== this.props.end_selected;
    },
 
    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return {__html: dt + " | " + doc.snippet.htext};
    },

    fake_markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return dt + " | " + doc.snippet.htext;
    },

    /**
    * Find the next sentence to render. Don't decide if it will fit yet
    */
    find_next: function(docs){
       let qf = _.filter(docs, function(d){
                   return d.snippet.has_q && d.snippet.has_f;
              }); 
       if (qf.length > 0){
            let out = qf[Math.floor(Math.random() * qf.length)];
            return out;
       }
       let q_or_f = _.filter(docs, function(d){return d.snippet.has_q || d.snippet.has_f});
       if (q_or_f.length > 0){
           let out = q_or_f[Math.floor(Math.random() * q_or_f.length)];
           return out;
       }
       return docs[Math.floor(Math.random() * docs.length)];
    },

    get_docs_to_render: function(){
        let docs = this.props.docs;
        docs = _.filter(docs, function(d) { 
                return moment(d.pubdate) > moment(this.props.start_selected, "YYYY-MM-DD") && 
                       moment(d.pubdate) < moment(this.props.end_selected, "YYYY-MM-DD")
        }, this);

        let render = [];
        let ht = 0; //height 
        if (docs.length > 0){
            while (ht < this.props.height && docs.length > 0){ //pretty hack-y. but apparently this is a weakness in react
                let picked = this.find_next(docs);
                _.remove(docs, function(doc) {
                    return doc.docid == picked.docid;
                });
                ht += this.fake_markup(picked).visualHeight();
                if (ht < this.props.height){          
                    render.push(picked);
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
        
        let docs;

        docs = this.get_docs_to_render();
        
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
            <Panel style={{backgroundColor: "white", overflowY: "hidden", height: this.props.height, overflow: "hidden"}}>
                {docs.map(function(doc, n) {
                    return <div key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/>;
                })}
           </Panel>
        );
       }
});
