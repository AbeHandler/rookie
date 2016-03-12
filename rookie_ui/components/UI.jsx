"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var moment = require('moment');

var DocViewer = require('./DocViewer.jsx');
var Status = require('./Status.jsx');
var Chart = require('./Chart.jsx');
var ChartTitle = require('./ChartTitle.jsx');
var SparklineGrid = require('./SparklineGrid.jsx');
var QueryBar = require('./QueryBar.jsx');
var TemporalStatus = require('./TemporalStatus.jsx');
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
    var width = ReactDOM.findDOMNode(this).offsetWidth;
    this.setState({width: width});
  },

  componentDidMount: function () {
    this.set_width();
    window.addEventListener("resize", this.set_width);
    window.addEventListener("keydown", this.handleKeyDown);
  },

  getInitialState(){
    //Notes.
    //1) convention: -1 == null
    return {drag_r: false, drag_l:false, width: 0, click_tracker: -1, chart_mode: "intro", all_results: [], start_selected:-1, end_selected:-1, f_counts:[], f: -1, hovered: -1, vars:this.props.vars, mode:"overview"};
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

  /**
  * This function will fire on mousedown if chart is in rectangle mode
  * starts the click timer
  */
  validClickTimer: function(){
    let start = +new Date();
    this.setState({click_tracker: start});
  },

  /**
  * This function will fire on mouseup if neither bar is clicked
  * @param {e_pageX} e_pageX location
  * @param {lateral_scale} d3 scale 
  * @param {pix_buffer} y-axis width + chart buffer. buffer is set in render method of UI.jsx
  */
  handle_mouse_up_in_rect_mode: function(e_pageX_adjusted, lateral_scale){
    let end = moment(this.state.end_selected, "YYYY-MM-DD");
    let start = moment(this.state.start_selected, "YYYY-MM-DD");
    let days_diff = start.diff(end, 'days');
    let half_of_span = Math.abs(Math.floor(days_diff/2));
    let clicked_here = moment(lateral_scale.invert(e_pageX_adjusted));
    clicked_here.subtract(half_of_span, 'days');
    let new_start = clicked_here.format("YYYY-MM-DD");
    clicked_here.add(half_of_span, 'days');
    clicked_here.add(half_of_span, 'days');
    let new_end = clicked_here.format("YYYY-MM-DD");
    console.log("to do fix offsets from width of rect");
    this.setState({start_selected:new_start,end_selected:clicked_here.format("YYYY-MM-DD")});
  },

  /**
  * This function will fire on mouseup if chart is in rectangle mode
  * determines what to do based on if it is a valid click
  */
  validClickEnd: function(e_page_X_adjusted){
    this.setState({drag_l: false, drag_r: false});
    if (this.state.click_tracker != -1){
      let d = +new Date() - this.state.click_tracker;
      let valid = true; //TODO: move the rect on click
      if (d > 250){
        valid = false;
      }
      this.setState({click_tracker: -1}, this.toggle_rect(e_page_X_adjusted, valid));
    }else{
      this.setState({click_tracker: -1});
    }
  },

  /**
  * The chart will now have drag_l is true
  */
  toggle_drag_start_l: function(){
    this.setState({drag_l : true});
  },

  /**
  * The chart will now have drag_r is true
  */
  toggle_drag_start_r: function(){
    this.setState({drag_r : true});
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
  * A clickhandler for sparkline time
  */
  clickTile: function (e) {
    let url = this.props.base_url + "get_docs?q=" + this.props.q + "&f=" + e + "&corpus=" + this.props.corpus;
        let minbin = _.head(this.props.chart_bins);
        let maxbin = _.last(this.props.chart_bins)
        $.ajax({
              url: url,
              dataType: 'json',
              cache: true,
              success: function(d) {
                let tmp = this.state.vars;
                this.setState({start_selected: minbin, end_selected: maxbin, f: e, mode: "docs", f_list: d["doclist"], f_counts: facet_datas[e]}, this.check_mode);
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
    let min;
    let max;
    min = moment(this.props.first_story_pubdate, "YYYY-MM-DD").format("YYYY-MM-DD"); 
    max = moment(this.props.last_story_pubdate, "YYYY-MM-DD").format("YYYY-MM-DD");
    this.setState({f: -1, mode:"overview", start_selected: min, end_selected: max});
  },

  /**
  * The UI starts in intro mode, which has sparklines. This turns on doc mode
  */
  turnOnDocMode: function(){
    if (this.state.f == -1){
        let url = this.props.base_url + "get_doclist?q=" + this.props.q + "&corpus=" + this.props.corpus;
        $.ajax({
              url: url,
              dataType: 'json',
              cache: true,
              success: function(d) {
                let tmp = this.state.vars;
                this.setState({f: -1, mode: "docs", all_results: d["doclist"], f_counts: []});
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
        });
    }else{
      this.setState({mode:"docs"});
    }
  },

  /**
  * The chart starts with no rectangle. This turns it on.
  */
  toggle_rect: function (p, valid) {
    let m = moment(p.toString());
    if (valid != false){
        let e = moment(this.state.end_selected);
        let s = moment(this.state.start_selected);
        let diff = moment.duration(e - s);
        let start = m.clone();
        let end = m.clone();
        end.add(diff);
        let min = moment(_.first(this.props.chart_bins), "YYYY-MM-DD"); 
        let max = moment(_.last(this.props.chart_bins), "YYYY-MM-DD");
        if (start < min) {
           start = min;
        }
        if (end > max) {
           end = max;
        } 
        this.setState({chart_mode:"rectangle", mode: "docs", start_selected:start, end_selected: end});
          if (this.state.f == -1){
              this.turnOnDocMode();
          }
        }
      else{
        if (this.state.chart_mode != "rectangle"){
          this.setState({chart_mode:"rectangle", drag_r: true, mode: "docs", start_selected:m.format("YYYY-MM-DD"), end_selected: m.format("YYYY-MM-DD")});
          this.turnOnDocMode();
        }
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
    let f = this.state.f;
    let q = this.props.q;
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

    let uiMonthHandler = this.handleMo;
    let b_f_click = this.handleLinguisticFacetClick;

    let handleMoUI = this.handleMo;

    var binned_counts_f = this.props.binned_counts_f;

    let chart_bins = this.props.chart_bins;
    let temporal_status = <TemporalStatus start_selected={this.state.start_selected} end_selected={this.state.end_selected}/>
    if (this.props.total_docs_for_q == 0){
        temporal_status = "";
    }
    let f_couts = this.state.f_counts;
    if (this.state.mode != "docs" & this.props.total_docs_for_q > 0){
      main_panel = <Panel>
                    <Status fX={this.fX} qX={qX} ndocs={this.props.total_docs_for_q} {...this.props}/>
                    <SparklineGrid {...this.props} clickTile={this.clickTile} q_data={q_data} col_no={3} facet_datas={this.props.facet_datas}/>
                   </Panel>
    } else { 
      let docviewer = <DocViewer f={this.state.f} handleBinClick={this.handleBinClick} start_selected={this.state.start_selected} end_selected={this.state.end_selected} all_results={this.state.all_results} docs={docs} bin_size={bin_size} bins={binned_facets}/>
      main_panel = <div>{temporal_status}{docviewer}</div>
    }
    let chart;
    if (this.props.total_docs_for_q > 0){
      let buffer = 5;
      chart = <Chart q={this.props.q} handle_mouse_up_in_rect_mode={this.handle_mouse_up_in_rect_mode} toggle_both_drags_start={() => this.setState({drag_l: true, drag_r: true}) } toggle_drag_start_l={this.toggle_drag_start_l} toggle_drag_start_r={this.toggle_drag_start_r} drag_l={this.state.drag_l} drag_r={this.state.drag_r} w={this.state.width - this.props.y_axis_width - buffer} buffer={buffer} y_axis_width={this.props.y_axis_width} mode={this.state.mode} validClickEnd={this.validClickEnd} validClickTimer={this.validClickTimer} toggle_rect={this.toggle_rect} chart_mode={this.state.chart_mode} qX={qX} set_date={this.set_date} set_dates={this.set_dates} start_selected={this.state.start_selected} end_selected={this.state.end_selected} {...this.props} f_data={f_couts} belowchart="50" height={this.state.width / this.props.w_h_ratio}  keys={chart_bins} datas={q_data}/>
      
    }else{
      chart = "";
    }


    return(
        <div>
            <QueryBar corpus={this.props.corpus}/>
             <Panel>
             <ChartTitle turnOnDocMode={this.turnOnDocMode} fX={this.fX} qX={qX} ndocs={this.props.total_docs_for_q} f={this.state.f} mode={this.state.mode} q={this.props.q}/>
             </Panel>
             {chart}
            <div>
              {main_panel}
            </div>

       </div>);
  }
});
