"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

var DocViewer = require('./DocViewer.jsx');
var Status = require('./Status.jsx');
var Chart = require('./Chart.jsx');
var IntroChart = require('./IntroChart.jsx');
var ChartTitle = require('./ChartTitle.jsx');
var SparklineGrid = require('./SparklineGrid.jsx');
var QueryBar = require('./QueryBar.jsx');
var TemporalStatus = require('./TemporalStatus.jsx');
var $ = require('jquery');
var Panel = require('react-bootstrap/lib/Panel');
//var ExampleInput = require('./ExampleInput.jsx')


module.exports = React.createClass({

  check_mode: function(){
    if (this.state.f != -1){
        this.setState({mode: "docs"});
    }else{
        this.setState({mode: "overview"});
    }
  },

  getInitialState(){
    //Notes.
    //1) convention: -1 == null
    let min = moment(_.first(this.props.chart_bins), "YYYY-MM-DD"); 
    let max = moment(_.last(this.props.chart_bins), "YYYY-MM-DD");
    let start = min.format("YYYY-MM-DD");
    let end = max.format("YYYY-MM-DD");
    return {click_tracker: -1, chart_mode: "intro", all_results: [], start_selected:start, end_selected:end, f_counts:[], f: -1, hovered: -1, vars:this.props.vars, mode:"overview"};
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

  validClickTimer: function(){
    let start = +new Date();
    this.setState({click_tracker: start});
  },

  validClickEnd: function(e){
    if (this.state.click_tracker != -1){
      let d = +new Date() - this.state.click_tracker;
      let valid = true;
      if (d > 250){
        valid = false;
      }
      this.setState({click_tracker: -1}, this.toggle_rect(e, valid));
    }else{
      this.setState({click_tracker: -1});
    }
  },

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
      if (d > start & d< max){
         this.setState({end_selected:d.format("YYYY-MM-DD")});
      }
    }
  },

  set_dates: function (start_date, end_date) {
    let s = moment(start_date);
    let e = moment(end_date);
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    if (s < e  & s > min & e < max) {
      this.setState({start_selected:s.format("YYYY-MM-DD"), end_selected:e.format("YYYY-MM-DD")});
    }
  },

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

  qX: function(){
    if (this.state.f != -1){
      location.href= this.props.base_url + '?q=' + this.state.f +'&corpus=' + this.props.corpus;
    }
  },

  fX: function(){
    let min;
    let max;
    min = moment(this.props.first_story_pubdate, "YYYY-MM-DD").format("YYYY-MM-DD"); 
    max = moment(this.props.last_story_pubdate, "YYYY-MM-DD").format("YYYY-MM-DD");
    this.setState({f: -1, mode:"overview", start_selected: min, end_selected: max});
  },

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

  toggle_rect: function (p, valid) {
    let m = moment(p.toString());
    if (valid != false){
        var f = moment(this.props.last_story_pubdate);
        var l = moment(this.props.first_story_pubdate);
        let diff = moment.duration(f.diff(l, 'days') / 10, 'days');
        let start = m.clone();
        let end = m.clone();
        start.subtract(diff);
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
        console.log("not a valid click");
      }
  },

  render: function() {
    let f = this.state.f;
    let q = this.props.q;
    let qX = this.qX;
    console.log(this.props.y_axis_width);
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

    let rw = {
        width: "100%",
    };

    let handleMoUI = this.handleMo;

    var binned_counts_f = this.props.binned_counts_f;

    let chart_bins = this.props.chart_bins;

    let f_couts = this.state.f_counts;
    if (this.state.mode != "docs" & this.props.total_docs_for_q > 0){
      main_panel = <Panel>
                    <Status fX={this.fX} qX={qX} ndocs={this.props.total_docs_for_q} {...this.props}/>
                    <SparklineGrid {...this.props} clickTile={this.clickTile} q_data={q_data} col_no={3} facet_datas={this.props.facet_datas}/>
                   </Panel>
    } else { 
      let docviewer = <DocViewer f={this.state.f} handleBinClick={this.handleBinClick} start_selected={this.state.start_selected} end_selected={this.state.end_selected} all_results={this.state.all_results} docs={docs} bin_size={bin_size} bins={binned_facets}/>
      main_panel = <div><TemporalStatus start_selected={this.state.start_selected} end_selected={this.state.end_selected}/>{docviewer}</div>
    }
    let chart;
    if (this.props.total_docs_for_q > 0){
      if (this.state.chart_mode != "intro"){
        chart = <Chart y_axis_width={this.props.y_axis_width} mode={this.state.mode} validClickEnd={this.validClickEnd} validClickTimer={this.validClickTimer} toggle_rect={this.toggle_rect} chart_mode={this.state.chart_mode} qX={qX} set_date={this.set_date} set_dates={this.set_dates} start_selected={this.state.start_selected} end_selected={this.state.end_selected} {...this.props} f_data={f_couts} belowchart="50" height={this.props.width / this.props.w_h_ratio}  keys={chart_bins} datas={q_data}/>
      }else{
        chart = <IntroChart y_axis_width={this.props.y_axis_width} mode={this.state.mode} toggle_rect={this.toggle_rect} qX={qX} set_date={this.set_date} start_selected={this.state.start_selected} end_selected={this.state.end_selected} {...this.props} f_data={f_couts} belowchart="50" height={this.props.width / this.props.w_h_ratio}  keys={chart_bins} datas={q_data}/>
      }
      
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
