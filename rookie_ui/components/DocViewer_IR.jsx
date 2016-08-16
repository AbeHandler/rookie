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
        if (this.props.experiment_mode){
            return {__html: "<a style='color:black; text-decoration:none'>" + doc.snippet.htext + "</a>"};
        }else{
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

    format_d: function(d){
        return moment(d).format("MMM. DD YYYY");
    },


    gettip: function(n, headline){
        return <Tooltip id={n}>{headline}</Tooltip>
    },

    getInitialState: function(){
        let per_page = 10;
        console.log("thisprops docs", this.props.docs);
        let pages = Math.floor(this.props.docs.length/per_page);
        return {page: 1, drag_r: false, PER_PAGE:per_page, pages: pages}
    },

    get_docs: function(results, page){
        let put = [];
        let i;
        for (i = 0; i < results.length; i++){
            if (i > (page * this.state.PER_PAGE) && (i < ((page * this.state.PER_PAGE) + this.state.PER_PAGE))){
                put.push(results[i]);
            }
        }
        return put;
    },

    increment_page: function () {
        let p = this.state.page + 1;
        this.setState({page: p});
        this.forceUpdate();
    },

    decrement_page: function () {
        let p = this.state.page - 1;
        this.setState({page: p});
        this.forceUpdate();
    },

    render: function(){

        console.log("docs", this.props.docs);
        if (this.props.docs.length < 1){
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
        let gettip = this.gettip;
        let previous_page = "";
        let next_page = "";
        let page = this.state.page;
        if (page > 1){
            previous_page = <div style={{float: "left", cursor: 'pointer', padding: '5px', borderRadius: '3cm', border: '1px solid grey'}} onClick={this.decrement_page} href="#">previous page</div>;
        }
        if (page < this.state.pages){
            next_page = <div style={{float: "right", cursor: 'pointer', padding: '5px', borderRadius: '3cm', border: '1px solid grey'}} onClick={this.increment_page} href="#">next page</div>;
        }

        let docs = this.get_docs(this.props.docs, page);
        console.log("docs", docs);

        return(
            <div>
                <div style={{width: "100%", height: "40px"}}>
                    <div style={{width: "15%", margin:"auto"}}>
                        {previous_page}
                        {next_page}
                    </div>
                </div>
                <div style={{backgroundColor: "white", overflowY: "hidden", overflow: "hidden"}}>
                    {docs.map(function(doc, n) {
                        return <div>
                                <div style={{fontWeight: "bold", color: "#1a0dab"}}>{doc.headline} | <span style={{color: "grey"}}>{format_d(doc.pubdate)}</span></div>
                                <span key={n} style={rowStyle} dangerouslySetInnerHTML={markup(doc)}/>
                                </div>
                                  
                    })}
               </div>
           </div>
        );
       }
});
