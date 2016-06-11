"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var moment = require('moment');

var DocViewer = require('./DocViewer_generic.jsx');
var SparklineStatus = require('./SparklineStatus.jsx');
var Chart = require('./Chart.jsx');
var ChartTitle = require('./ChartTitle.jsx');
var SparklineGrid = require('./SparklineGrid.jsx');
var QueryBar = require('./QueryBar.jsx');
var SummaryStatus = require('./SummaryStatus.jsx');
var $ = require('jquery');
var Panel = require('react-bootstrap/lib/Panel');


module.exports = React.createClass({

  check_mode: function(){
    if (this.state.f != -1){
        this.setState({mode: "docs"});
    }else{
        this.setState({mode: "overview"});
    }
  },

  set_width: function(){
    var width = $(window).width();
    var height = $(window).height();
    this.setState({width: width, height: height});
  },

  toggleIntro: function(){
    this.setState({mode: "overview", chart_mode: "intro", kind_of_doc_list: "summary_baseline"});
  },

  componentDidMount: function () {
    this.set_width();
    window.addEventListener("resize", this.set_width);
    window.addEventListener("keydown", this.handleKeyDown);
  },

  getInitialState(){
    //Notes.
    //convention: -1 == null
    return {drag_r: false, drag_l:false, mouse_down_in_chart: false,
           mouse_is_dragging: false, width: 0, height: 0, click_tracker: -1,
           chart_mode: "intro", all_results: [], start_selected:-1,
           end_selected:-1, f_counts:[], f: -1, hovered: -1,
           //current_bin_position: -1,
           kind_of_doc_list: "summary_baseline",
           vars:this.props.vars, mode:"overview"};
  },

  resetT: function(){
    this.setState({start_selected: -1, end_selected: -1, mode:"overview", chart_mode: "intro"});
  },

  resultsToDocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list;
    }
    let start = moment(this.state.start_selected, "YYYY-MM-DD");
    let end = moment(this.state.end_selected, "YYYY-MM-DD");
    let out_results =  _.filter(results, function(value, key) {
        //dates come from server as YYYY-MM-DD
        if (moment(value.pubdate, "YYYY-MM-DD").isAfter(start) || moment(value.pubdate, "YYYY-MM-DD").isSame(start)){
          if (moment(value.pubdate, "YYYY-MM-DD").isBefore(end) || moment(value.pubdate, "YYYY-MM-DD").isSame(end)){
            return true;
          }
        }
        return false;
    });
    return out_results;

  },

  mouse_move_in_chart: function(p){
    this.check_drag(p);
    //this.setState({current_bin_position: moment(p).format("YYYY-MM")}, );
  },

  check_drag: function(p) {
    if (this.state.mouse_down_in_chart){
      if (this.state.drag_l == false && this.state.drag_r == false){
        let start = moment(p).format("YYYY-MM-DD");
        let end = moment(p).format("YYYY-MM-DD");
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
  * This function will fire on mousedown if chart is in rectangle mode
  */
  mouse_down_in_chart_true: function(d){
    this.setState({
      mouse_down_in_chart: true, mouse_is_dragging: true}, function(){
        if (this.state.drag_l == false && this.state.drag_r == false){
          this.set_dates(d, d);
        }
      });
  },

  /**
  * This function will fire on mouseup if chart is in rectangle mode
  * determines what to do based on if it is a valid click
  */
  mouse_up_in_chart: function(e_page_X_adjusted){
    this.setState({drag_l: false, drag_r: false, mouse_down_in_chart: false, mouse_is_dragging: false});
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
      let end = moment(this.state.end_selected, "YYYY-MM-DD");
      let min = moment(this.props.chart_bins[0]);
      if ((d < end) &  (d>min)){
        this.setState({start_selected:d.format("YYYY-MM-DD")});
      }
    }
    if (start_end == "end"){
      let start = moment(this.state.start_selected, "YYYY-MM-DD");
      let max = moment(this.props.chart_bins[this.props.chart_bins.length -1]);
      if (d > start & d < max){
         this.setState({end_selected:d.format("YYYY-MM-DD")});
      }
    }
  },

  /**
  * Set both dates at once: start and end
  */
  set_dates: function (start_date, end_date) {
    let s = moment(start_date);
    let e = moment(end_date);
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    if (s < e  & s > min & e < max) {
      this.setState({start_selected:s.format("YYYY-MM-DD"), end_selected:e.format("YYYY-MM-DD")});
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
                this.setState({start_selected: minbin,
                              end_selected: maxbin,
                              f: e,
                              mode: "docs",
                              f_list: d,
                              chart_mode: "intro",
                              f_counts: facet_datas[e]}, this.check_mode);
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
    this.setState({f: -1, mode:"overview", start_selected: -1, end_selected: -1, f_counts: []});
  },

  /**
  * The UI starts in intro mode, which has sparklines. This turns on doc mode
  */
  turnOnDocMode: function(){
    if (this.state.f == -1){
        let url = this.props.base_url + "get_sents?q=" + this.props.q + "&corpus=" + this.props.corpus;
        $.ajax({
              url: url,
              dataType: 'json',
              cache: true,
              success: function(d) {
                let minbin = _.head(this.props.chart_bins);
                let maxbin = _.last(this.props.chart_bins);
                if (this.state.mode == "overview"){
                        this.setState({kind_of_doc_list: "no_summary", chart_mode: "intro", start_selected: minbin, end_selected: maxbin, f: -1, mode: "docs", all_results: d, f_counts: []});
                }
                if (this.state.chart_mode == "rectangle"){
                        this.setState({f: -1, mode: "docs", all_results: d, f_counts: []});
                }
                this.forceUpdate();
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
        });
    }
  },

  turn_on_rect_mode: function(p){
    this.setState({chart_mode:"rectangle", start_selected: -1, end_selected: -1, mouse_down_in_chart:true, mode: "docs"});
    if (this.state.f == -1){
        this.turnOnDocMode();
    }
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
          new_start = moment(this.state.start_selected).add(1, granularity).format("YYYY-MM-DD");
          new_end = moment(this.state.end_selected).add(1, granularity).format("YYYY-MM-DD");
        }
        if(e.keyIdentifier == "Left"){
          new_start = moment(this.state.start_selected).subtract(1, granularity).format("YYYY-MM-DD");
          new_end = moment(this.state.end_selected).subtract(1, granularity).format("YYYY-MM-DD");
        }
        this.setState({start_selected:new_start, end_selected: new_end});
      }
    }
  },

  render: function() {
    let qX = this.qX;
    let bin_size = "year"; //default binsize
    // docs = those that match q, f & t. all_results = what comes from browser.
    let docs = this.resultsToDocs(this.state.all_results);

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
    let temporal_status = <SummaryStatus resetT={this.resetT} kind_of_doc_list={this.state.kind_of_doc_list} ndocs={docs.length} turnOnSummary={() => this.setState({kind_of_doc_list: "summary_baseline"})} turnOnDoclist={() => this.setState({kind_of_doc_list: "no_summary"})} start_selected={this.state.start_selected} end_selected={this.state.end_selected}/>
    if (this.props.total_docs_for_q == 0){
        temporal_status = "";
    }
    let chart_height = this.state.width / this.props.w_h_ratio;
    let query_bar_height = 50;
    let lower_h = this.state.height - chart_height - query_bar_height - 300;
    main_panel = <Panel>
                    <SparklineStatus fX={this.fX} qX={qX} ndocs={this.props.total_docs_for_q} {...this.props}/>
                    <SparklineGrid ntile="10" width={this.state.width/2}
                                   height={lower_h} f={this.state.f}
                                   {...this.props} clickTile={this.clickTile}
                                   q_data={q_data} col_no={1}
                                   facet_datas={this.props.facet_datas}/>
                   </Panel>
    let chart;
    let docviewer = <DocViewer kind_of_doc_list={this.state.kind_of_doc_list}
                                height={lower_h + 50}
                                f={this.state.f}
                                mode={this.state.mode}
                                handleBinClick={this.handleBinClick}
                                start_selected={this.state.start_selected}
                                end_selected={this.state.end_selected}
                                all_results={this.state.all_results}
                                docs={docs} bin_size={bin_size}
                                bins={binned_facets}/>
    if (this.props.total_docs_for_q > 0){
      let buffer = 5;
      chart = <Chart
               tooltip_width="90"
               turn_on_rect_mode={this.turn_on_rect_mode}
               mouse_move_in_chart={this.mouse_move_in_chart}
               f={this.state.f}
               q={this.props.q}
               handle_mouse_up_in_rect_mode={this.handle_mouse_up_in_rect_mode}
               toggle_both_drags_start={() => this.setState({drag_l: true, drag_r: true}) }
               toggle_drag_start_l={this.toggle_drag_start_l}
               toggle_drag_start_r={this.toggle_drag_start_r}
               drag_l={this.state.drag_l}
               drag_r={this.state.drag_r}
               w={this.state.width - this.props.y_axis_width - buffer}
               buffer={buffer}
               y_axis_width={this.props.y_axis_width}
               mode={this.state.mode}
               mouse_up_in_chart={this.mouse_up_in_chart}
               mouse_down_in_chart_true={this.mouse_down_in_chart_true}
               chart_mode={this.state.chart_mode}
               qX={qX} set_date={this.set_date}
               set_dates={this.set_dates}
               start_selected={this.state.start_selected}
               end_selected={this.state.end_selected}
               {...this.props}
               f_data={this.state.f_counts}
               belowchart="50"
               height={chart_height}
               keys={chart_bins}
               datas={q_data}/>

    }else{
      chart = "";
    }

    return(
        <div>
            <QueryBar height={query_bar_height}
                      q={this.props.q}
                      corpus={this.props.corpus}/>
             <Panel>
             <ChartTitle f_docs={docs}
                         chartMode={this.state.chart_mode}
                         toggleIntro={this.toggleIntro}
                         turnOnDocMode={this.turnOnDocMode}
                         fX={this.fX} qX={qX}
                         ndocs={this.props.total_docs_for_q}
                         f={this.state.f}
                         mode={this.state.mode}
                         q={this.props.q}/>
             </Panel>
             {chart}
            <div style={{float:"left", width:(this.state.width-5)/2}}>
              {main_panel}
            </div>
            <div style={{float:"right", width:(this.state.width-5)/2}}>
              {docviewer}
            </div>

       </div>);
  }
});
