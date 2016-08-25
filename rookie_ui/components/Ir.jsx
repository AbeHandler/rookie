"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var moment = require('moment');
require('moment-round');
var DatePicker = require('react-datepicker');
var SummaryStatus = require('./SummaryStatus.jsx');
var DocViewer = require('./DocViewer_IR.jsx');
var SparklineStatus = require('./SparklineStatus.jsx');
var Chart = require('./Chart.jsx');
var ChartTitle = require('./ChartTitle.jsx');
var SparklineGrid = require('./SparklineGrid.jsx');
var QueryBar = require('./QueryBar.jsx');
var $ = require('jquery');
var Panel = require('react-bootstrap/lib/Panel');
var Button = require('react-bootstrap/lib/Button');
var ButtonToolbar = require('react-bootstrap/lib/ButtonToolbar');


let q_color = "#0028a3";
let f_color = "#b33125";

module.exports = React.createClass({

  set_width: function(){
    var width = $(window).width();
    var height = $(window).height();
    this.setState({width: width, height: height});
  },



  componentDidMount: function () {
    this.set_width();
    window.addEventListener("resize", this.set_width);
    window.addEventListener("keydown", this.handleKeyDown);
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");

  },

  pageupdate: function(param){
    let tmp = param + this.state.summary_page;
    this.setState({summary_page:tmp}, function(){
      let dates = {start_selected: this.state.start_selected,
                   end_selected: this.state.end_selected}
      $.get("/log?pageupdate||param=" + param.toString() + "&dates=" + JSON.stringify(dates) + "runid=" + this.props.runid + "&date=" + n +  "&summary_page=" + this.state.summary_page);
    });
  },

  getInitialState(){
    //Notes.
    //convention: -1 == null
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    return {drag_r: false,
           drag_l:false,
           startDate: moment(),
           mouse_down_in_chart: false,
           mouse_is_dragging: false, width: 0,
           height: 0, click_tracker: -1,
           chart_mode: "intro",
           all_results: this.props.sents,
           start_selected:min,
           end_selected:max,
           summary_page:0,
           f_counts:this.props.f_counts,
           f: this.props.f,
           f_list: this.props.f_list,
           startdisplay: 0, //rank of first facet to display... i.e offset by?
           //current_bin_position: -1,
           kind_of_doc_list: "no_summary",
           facet_datas: this.props.facet_datas,
           mode:"docs"};
  },

  //do you show a little x in the summary box status?
  show_x_for_t_in_sum_status: function(){
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    if (this.state.start_selected == min && this.state.end_selected == max){
      return false;
    }else{
      return true;
    }
  },

  resetT: function(){
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    this.setState({start_selected: min,
                  end_selected: max,
                  chart_mode: "intro",
                  facet_datas: []});

  },

  resultsToDocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list;
    }
    let start = moment(this.state.start_selected, "YYYY-MM");
    let end = moment(this.state.end_selected, "YYYY-MM");
    let out_results =  _.filter(results, function(value, key) {
        //dates come from server as YYYY-MM

        if (moment(value.pubdate, "YYYY-MM").isAfter(start) || moment(value.pubdate, "YYYY-MM").isSame(start)){
          if (moment(value.pubdate, "YYYY-MM").isBefore(end) || moment(value.pubdate, "YYYY-MM").isSame(end)){
            return true;
          }
        }
        return false;
    });
    return out_results;
    return _.sortBy(out_results, function(o) { return o.search_engine_index_doc; });
  },

  n_fdocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list;
        return results.length;
    }else{
      return 0;
    }
  },

  mouse_move_in_chart: function(p){
    if (this.state.mouse_down_in_chart){
      if (this.state.drag_l == false && this.state.drag_r == false){
        let start = moment(p).format("YYYY-MM");
        let end = moment(p).format("YYYY-MM");
        if (start === end)
        this.setState({mouse_is_dragging: true,
                      drag_l: false,
                      drag_r: true,
                      mode: "docs",
                      start_selected: start,
                      end_selected: end});
      }
    }
  },

  /**
  * This function will fire on mouseup if chart is in rectangle mode
  */
  mouse_up_in_chart: function(e_page_X_adjusted){
    if (this.state.start_selected == -1 && this.state.end_selected == -1){
      let s = moment(e_page_X_adjusted).add(-1, 'month');
      let e = moment(e_page_X_adjusted).add(1, 'month');
      s = s.format("YYYY-MM");
      e = e.format("YYYY-MM");

      this.setState({start_selected:s,end_selected:e});
    }else{
      let url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + this.state.start_selected + "&enddate=" + this.state.end_selected;

      let max = this.props.chart_bins[this.props.chart_bins.length - 1];


      if(this.state.start_selected === this.state.end_selected){
        if (moment(max) > moment(this.state.end_selected, "YYYY-MM")){
          let e = moment(this.state.end_selected, "YYYY-MM");
          e.add(1, "months");
          this.setState({end_selected:e.format("YYYY-MM")});
          url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + this.state.start_selected + "&enddate=" + e.format("YYYY-MM");
        }
      }

    }

    this.setState({drag_l: false, drag_r: false,
                   mouse_down_in_chart: false, mouse_is_dragging: false});
  },

  turnoff_drag: function(){
    this.setState({drag_l: false, drag_r: false,
                   mouse_down_in_chart: false, mouse_is_dragging: false});
  },

  /**
  * The chart will now have drag_l is true
  */
  toggle_drag_start_l: function(){
    this.setState({drag_l : true, mouse_is_dragging: true});
  },

  /**
  * The chart will now have drag_r is true
  */
  toggle_drag_start_r: function(){
    this.setState({drag_r : true, mouse_is_dragging: true});
  },

  /**
  * Set one of the dates: a start or end
  */
  set_date: function (date, start_end) {
    let d = moment(date);

    if (start_end == "start"){
      let end = moment(this.state.end_selected, "YYYY-MM");
      let min = moment(this.props.chart_bins[0]);
      if ((d < end) &  (d>min)){

        this.setState({start_selected:d.format("YYYY-MM")});

      }
    }
    if (start_end == "end"){
      let start = moment(this.state.start_selected, "YYYY-MM");

      let max = moment(this.props.chart_bins[this.props.chart_bins.length -1]);

      if (d > start & d < max){
         this.setState({end_selected:d.format("YYYY-MM")});
      }
    }
  },

  /**
  * A clickhandler for sparkline tile
  */
  clickTile: function (e) {
    let url = this.props.base_url + "get_sents?q=" + this.props.q + "&f=" + e + "&corpus=" + this.props.corpus;
        let minbin = _.head(this.props.chart_bins);
        let maxbin = _.last(this.props.chart_bins);
        $.ajax({
              url: url,
              dataType: 'json',
              cache: true,
              success: function(d) {
                //count vector for just clicked facet, e (event)
                let fd = _.find(this.state.facet_datas, function(o) { return o.f == e; });
                this.setState({
                              f: e,
                              mode: "docs",
                              f_list: d,
                              f_counts: fd["counts"]});

              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
        });
  },

  /**
  * A handler for when user clicks the X by Q. Requery with F equal to Q
  */
  qX: function(){
    if (this.state.f != -1){
      location.href= this.props.base_url + '?q=' + this.state.f +'&corpus=' + this.props.corpus;
    }
  },

  /**
  * A handler for when user clicks the X by F. Adjust state so f=-1
  */
  fX: function(){
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);

    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");

    this.setState({f: -1,
                   mode:"overview",
                   //start_selected: -1,
                   chart_mode: "intro",
                   end_selected: -1,
                   start_selected:min,
                   end_selected:max,
                   f_counts: []});
  },

  turn_on_rect_mode: function(p){
    this.setState({chart_mode:"rectangle",
                  start_selected:-1,
                  end_selected:-1,
                  mouse_down_in_chart:true,
                  mode: "docs"});
  },

  /**
  * Handle key press in the whole UI.

  TODO: QueryBar.jsx has its own click handler for enter key. should probably be moved here
  */
  handleKeyDown: function(e){
    if (this.state.start_selected != -1 && this.state.end_selected != -1){
      let new_end, new_start;
      let granularity = "weeks"; //TODO: this won't scale if span changes
      if (e.keyIdentifier == "Right" || e.keyIdentifier == "Left"){
          if(e.keyIdentifier == "Right"){
            new_start = moment(this.state.start_selected).add(1, granularity).format("YYYY-MM");
            new_end = moment(this.state.end_selected).add(1, granularity).format("YYYY-MM");
          }
          if(e.keyIdentifier == "Left"){
            new_start = moment(this.state.start_selected).subtract(1, granularity).format("YYYY-MM");
            new_end = moment(this.state.end_selected).subtract(1, granularity).format("YYYY-MM");
          }
          this.setState({start_selected:new_start, end_selected: new_end});

        let url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + new_start + "&enddate=" + new_end;

        if (this.state.f == -1){
          $.ajax({
                      url: url,
                      dataType: 'json',
                      cache: true,
                      method: 'GET',
                      success: function(d) {
                        //count vector for just clicked facet, e (event)
                        this.setState({facet_datas: d["d"], startdisplay: 0});
                      }.bind(this),
                      error: function(xhr, status, err) {
                        console.error(this.props.url, status, err.toString());
                      }.bind(this)
          });
        }


      }
    }
  },

  requery: function (arg) {
      location.href= '/?q='+ arg + '&corpus=' + this.props.corpus;
  },

  /**
  make the status bar for the summary box
  */
  summary_status: function(){
    let docs = this.resultsToDocs(this.state.all_results);
    let show_x_for_t_in_sum_status = this.show_x_for_t_in_sum_status();
    let maxpages = Math.ceil(docs.length/this.props.docsperpage);
    let out = <SummaryStatus resetT={this.resetT}
              show_summarize={false}
              show_x = {show_x_for_t_in_sum_status}
              kind_of_doc_list={this.state.kind_of_doc_list}
              ndocs={docs.length}
              q={this.props.q}
              f={this.state.f}
              page={this.state.summary_page}
              q_color="#1a0dab"
              f_color={f_color}
              maxpages={maxpages}
              pageupdate={this.pageupdate}
              turnOnSummary={() => this.setState({kind_of_doc_list: "summary_baseline"})}
              turnOnDoclist={() => this.setState({kind_of_doc_list: "no_summary"})}
              start_selected={this.state.start_selected}
              end_selected={this.state.end_selected}/>
    return out;
  },

  /**
  make the status bar for the sparkline panel
  */
  sparkline_status: function(){
      let backbutton = "";
      if (this.state.startdisplay > 0){
          backbutton = <span  style={{ textDecoration: "underline", float:"left", cursor: "pointer", paddingRight: "7px"}} onClick={()=>this.setState({startdisplay: this.state.startdisplay - this.props.sparkline_per_panel})} bsSize="xsmall">back</span>
      }
      let moresubjects = "";
       if ((this.state.startdisplay/this.props.sparkline_per_panel + 1) < (Math.floor(global_facets.length/this.props.sparkline_per_panel) + 1)){
          moresubjects = "more subjects"
      }
      return <div>
                     <SparklineStatus fX={this.fX} qX={this.qX}
                     ndocs={this.props.total_docs_for_q}
                     {...this.props}/>

                     <div style={{float:"right", marginTop: "-5px"}}>
                      <div style={{backgroundColor:"green", height:"50%"}}>
                          <span style={{ float:"left",  height: "50%"}}>
                            {backbutton}
                          </span>
                          <span style={{ textDecoration: "underline", float:"right", cursor: "pointer"}} onClick={()=>this.setState({startdisplay: this.state.startdisplay + this.props.sparkline_per_panel})} bsSize="xsmall">
                            {moresubjects}
                          </span>

                      </div>
                      <div style={{color:"#808080", fontSize: "10px", float:"right", height:"50%"}}>
                        {"page " + (this.state.startdisplay/this.props.sparkline_per_panel + 1) + " of " + (Math.floor(global_facets.length/this.props.sparkline_per_panel) + 1)}
                      </div>
                      </div>
                     </div>
  },

  onsubmit: function(e){
      window.location = "/quiz?current=tool&runid=" + this.props.runid + "&q=5&answer=" + e + "&start=" + this.props.start + "&end=" + window.timestamp();
  },

  setstart: function(date) {
     this.setState({
       start_selected: date.format('YYYY-MM')
     });
   },
   setend: function(date) {
   this.setState({
     end_selected: date.format('YYYY-MM')
   });
 },

  render: function() {

    let docs = this.resultsToDocs(this.state.all_results);
    let docs_ignoreT = this.n_fdocs(this.state.all_results);
    let y_scroll = {
        overflowY: "scroll",
        height:this.props.height
    };
    let binned_facets = _.sortBy(this.props.binned_facets, function(item) {
        return parseInt(item.key);
    });
    let selected_binned_facets;

    let row_height = Math.floor(this.props.height/binned_facets.length);

    let main_panel;

    let chart_bins = this.props.chart_bins;
    let summary_status = this.summary_status();
    if (this.props.total_docs_for_q == 0 ){
        summary_status = "";
    }
    let chart_height = this.state.width / this.props.w_h_ratio;
    let query_bar_height = 50;
    let lower_h = (this.state.height - chart_height - query_bar_height)/2.5;

    let sparkline_h = this.sparkline_status();
    let end_facet_no = this.state.startdisplay + this.props.sparkline_per_panel


    main_panel = <Panel header={sparkline_h}>
                                   <SparklineGrid startdisplay={this.state.startdisplay}
                                   enddisplay={end_facet_no}
                                   width={this.state.width/2}
                                   height={lower_h}
                                   f={this.state.f}
                                   w_h_ratio={this.props.w_h_ratio}
                                   clickTile={this.clickTile}
                                   q_data={q_data} col_no={1}
                                   facet_datas={this.state.facet_datas}/>
                   </Panel>

    let docviewer = <DocViewer kind_of_doc_list={this.state.kind_of_doc_list}
                                height={lower_h + 50}
                                f={this.state.f}
                                mode={this.state.mode}
                                handleBinClick={this.handleBinClick}
                                start_selected={this.state.start_selected}
                                end_selected={this.state.end_selected}
                                all_results={this.state.all_results}
                                docs={docs}
                                runid={this.props.runid}
                                page={this.state.summary_page}
                                per_page={this.props.docsperpage}
                                experiment_mode={this.props.experiment_mode}
                                per_page={this.props.docsperpage}
                                bins={binned_facets}/>

                              let answers = this.props.answers;

    return(
        <div>
            <QueryBar height={query_bar_height}
                      q={this.props.q}
                      experiment_mode={this.props.experiment_mode}
                      corpus={this.props.corpus}/>
                    <Panel style={{width:"100%"}}>
                        <div style={{width:"40%", margin: "auto"}}>
                        <span style={{float:"left"}}><span style={{marginRight:"10px", fontWeight: "bold"}}>Start</span><span style={{borderTop:"1px solid black"}}><DatePicker minDate={moment("1987-01")} maxDate={moment(this.state.end_selected)} selected={moment(this.state.start_selected)} onChange={this.setstart} /></span></span>
                        <span style={{float:"right"}}><span style={{marginRight:"10px", fontWeight: "bold"}}>End</span><span style={{borderTop:"1px solid black"}}><DatePicker minDate={moment(this.state.start_selected)} maxDate={moment("2007-12")}  selected={moment(this.state.end_selected)} onChange={this.setend} /></span></span>
                        </div>
                  </Panel>
            <div style={{width:(this.state.width-5)}}>
              <Panel header={summary_status}>
                <div style={{"width":"100%"}}>
                  {docviewer}
                </div>
              </Panel>
            </div>
       </div>
        );
  }
});
