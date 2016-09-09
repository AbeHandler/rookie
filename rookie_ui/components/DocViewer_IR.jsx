"use strict";
/*
Doc viewer _ trial
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var $ = require('jquery');
var Panel = require('react-bootstrap/lib/Panel');
var OverlayTrigger = require('react-bootstrap/lib/OverlayTrigger');
var Button = require('react-bootstrap/lib/Button');
var Tooltip = require('react-bootstrap/lib/Tooltip');
var Modal = require('./Modal.jsx');


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
            || nextProps.page != this.props.page
            || nextProps.width != this.props.width;
    },


    //need to use this markup thing b/c snippet has html in it
    markup: function(doc) {
        let dt = moment(doc.pubdate, "YYYY-MM-DD").format("MM.DD.YYYY");
        return {__html: "<a style='color:black;'>" + doc.snippet.htext + "</a>"};
    },

    format_d: function(d){
        return moment(d).format("MMM. DD YYYY");
    },

    gettip: function(n, headline){
        return <Tooltip id={n}>{headline}</Tooltip>
    },

    get_docs: function(results, page){
        let docs = this.props.docs;
        let render = [];
        let i;
        let start = this.props.page * this.props.per_page;
        let end = (this.props.page * this.props.per_page) + this.props.per_page;
        if (end > docs.length){
          end = docs.length;
        }
        if (docs.length > 0){
            for(i = start; i < end; i++){
                render.push(docs[i]);
            }
        }
        return render;
    },

    render: function(){

        if (this.props.docs.length < 1){
            return <div></div>;
        }
        let f = this.props.f;

        let props = this.props;
        let markup = this.markup;
        let format_d = this.format_d;
        let gettip = this.gettip;
        let docs = this.get_docs(this.props.docs, this.props.page);

        return(
            <div>
                <div style={{backgroundColor: "white", overflowY: "hidden", overflow: "hidden"}}>
                    {docs.map(function(doc, n) {
                        return <div>
                                <div onClick={() => props.select(doc.docid, doc.pubdate)} style={{fontWeight: "bold", color: "#1a0dab"}}>{doc.headline} | <span style={{color: "grey"}}>{format_d(doc.pubdate)}</span></div>
                                <span onClick={() => props.select(doc.docid, doc.pubdate)} key={n} style={{width:"100%", overflow:"hidden"}} dangerouslySetInnerHTML={markup(doc)}/>
                                </div>

                    })}
               </div>
           </div>
        );
       }
});
