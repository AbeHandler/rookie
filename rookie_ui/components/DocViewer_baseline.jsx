"use strict";
/*
Doc viewer _ trial
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var Panel = require('react-bootstrap/lib/Panel');
var OverlayTrigger = require('react-bootstrap/lib/OverlayTrigger');
var Button = require('react-bootstrap/lib/Button');
var Tooltip = require('react-bootstrap/lib/Tooltip');

module.exports = React.createClass({

    // need to avoid constantly updating the summary box.
    // feels glitchy if not limit update
    shouldComponentUpdate: function(nextProps, nextState) {
      return nextProps.all_results != this.props.all_results
            || nextProps.start_selected != this.props.start_selected
            || nextProps.end_selected != this.props.end_selected
            || nextProps.mode != this.props.mode
            || nextProps.f != this.props.f
            || nextProps.height != this.props.height
            || nextProps.width != this.props.width;
    },


    //need to use this markup thing b/c snippet has html in it
    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        console.log(this.props.static_mode);
        if (this.props.static_mode){
            return {__html: "<span style='color:black;' >" + doc.snippet.htext + "</span>"};
        }
        else{
            return {__html: "<a style='color:black;' href='" + doc.url + "' target='_blank' >" + doc.snippet.htext + "</a>"};
        }
        
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
            return render; // I Think dont sort by pubdate. Sort by goodness .... _.sortBy(render, function(d){ return moment(d.pubdate);});
        }else{
            return [];
        }

    },

    format_d: function(d){
        return moment(d).format("MMM. DD YYYY");
    },


    gettip: function(n, headline){
        return <Tooltip id={n}>{headline}</Tooltip>
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
            overflow:"hidden",
        };
        let markup = this.markup;
        let format_d = this.format_d;
        let gettip = this.gettip;
        return(
            <div style={{backgroundColor: "white", overflowY: "hidden", height: this.props.height, overflow: "hidden"}}>
                {docs.map(function(doc, n) {
                    return  <OverlayTrigger
                                overlay={gettip(n, doc.headline)} placement="top"
                                delayShow={300} delayHide={150}
                              >
                                <div style={{borderBottom:"1px solid lightgrey", paddingBottom: "3px"}}><span style={{color: "grey"}}>{format_d(doc.pubdate)} | </span><span key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/></div>
                              </OverlayTrigger>
                })}
           </div>
        );
       }
});
