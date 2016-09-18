"use strict";
/*
Doc viewer _ trial
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var Panel = require('react-bootstrap/lib/Panel');
var $ = require('jquery');
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
            || nextProps.page != this.props.page
            || nextProps.height != this.props.height
            || nextProps.width != this.props.width;
    },


    //need to use this markup thing b/c snippet has html in it
    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return {__html: "<a style='color:black;' >" + doc.snippet.htext + "</a>"};
    },

    fake_markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return dt + " | " + doc.snippet.htext;
    },

    /**
    * order the sentences for display
    */
    order: function(docs){
       let qf = _.filter(docs, function(d){
                   return d.snippet.has_q && d.snippet.has_f;
              });
       qf = _.sortBy(qf, function(o) { return o.hash; });
       let q_or_f = _.filter(docs, function(d){return (d.snippet.has_q || d.snippet.has_f)
                                                       && !(d.snippet.has_q && d.snippet.has_f)
                                               });
       q_or_f = _.sortBy(q_or_f, function(o) { return o.hash; });
       docs = _.sortBy(docs, function(o){return o.hash;});
       return qf.concat(q_or_f).concat(docs);
    },

    get_docs_to_render: function(){
        let docs = this.props.docs;
        let render = [];
        let ht = 0; //height
        let start = this.props.page * this.props.per_page;
        let end = (this.props.page * this.props.per_page) + this.props.per_page;
        if (end > docs.length){
          end = docs.length;
        }

        render = this.order(docs);


        //find the docs on the current page
        let out = [];
        if (render.length > 0){
            for(var i = start; i < end; i++){
                out.push(render[i]);
            }
        }

        return out;

    },

    format_d: function(d){
        return moment(d).format("MMM. DD YYYY");
    },

    gettip: function(n, headline){
        return <Tooltip id={n}>{headline}</Tooltip>
    },

    render: function(){

        let docs;
        let dates = {"start_selected": this.props.start_selected, "end_selected": this.props.end_selected}
        $.get("/log?runid=" + this.props.runid + "&date=" + window.timestamp() +  "&data=" + JSON.stringify(dates));
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
            <div style={{backgroundColor: "white", overflowY: "scroll", height: this.props.height}}>
                {docs.map(function(doc, n) {
                    return  <OverlayTrigger
                                overlay={gettip(n, doc.headline)} placement="top"
                                delayShow={300} delayHide={150}
                              >
                                <div style={{borderBottom:"1px solid lightgrey", paddingBottom: "3px"}}><span onClick={() => props.select(doc.docid, doc.pubdate)}  style={{color: "grey"}}>{format_d(doc.pubdate)} | </span><span onClick={() => props.select(doc.docid, doc.pubdate)} key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/></div>
                              </OverlayTrigger>
                })}
           </div>
        );
       }
});
