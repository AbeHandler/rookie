"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

var BinnedLinguisticFacets = require('./BinnedLinguisticFacets.jsx');
var GlobalFacetList = require('./GlobalFacetList.jsx');
var TemporalFacets = require('./TemporalFacets.jsx');
var DocViewer = require('./DocViewer.jsx');
var Status = require('./Status.jsx');
var Chart = require('./Chart.jsx');
var ChartTitle = require('./ChartTitle.jsx');
var SparklineGrid = require('./SparklineGrid.jsx');
var QueryBar = require('./QueryBar.jsx');
var $ = require('jquery');
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
    //2) keeping track of y/mo/dy is annoying but react won't allow object as prop
    let min;
    let max;
    min = moment(_.first(this.props.chart_bins), "YYYY-MM-DD"); 
    max = moment(_.last(this.props.chart_bins), "YYYY-MM-DD");
    let start = min.format("YYYY-MM-DD");
    let end = max.format("YYYY-MM-DD");
    //TODO: if no results, this fails
    return {start_selected:start, end_selected:end, f_counts:[], f: -1, hovered: -1, vars:this.props.vars, yr_start:min.format("YYYY"), mo_start:min.format("MM"), dy_start:min.format("DD"), yr_end:max.format("YYYY"), mo_end:max.format("MM"), dy_end:max.format("DD"), mode:"overview"};
  },

  resultsToDocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list; 
    }
    let start = moment(this.state.mo_start + "-" + this.state.dy_start + "-" +  this.state.yr_start, "MM-DD-YYYY");
    let end = moment(this.state.mo_end + "-" + this.state.dy_end + "-" +  this.state.yr_end, "MM-DD-YYYY");
    let tmp = _.filter(results, function(value, key) {
        //dates come from server as YYYY-MM-DD
        if (moment(value.pubdate, "YYYY-MM-DD").format("YYYY") == "2014"){
          if (moment(value.pubdate, "YYYY-MM-DD").format("MM") == "06"){        
            return true;
          }
        }
        return false;
    });
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

  set_date: function (date, start_end) {
    let d = moment(date).format("YYYY-MM-DD");
    if (start_end == "start"){
      this.setState({start_selected:d});
    }
    if (start_end == "end"){
      this.setState({end_selected:d});
    }
  },

  clickTile: function (e) {
    let url = "/get_docs?q=" + this.props.q + "&f=" + e + "&corpus=" + this.props.corpus;
        $.ajax({
              url: url,
              dataType: 'json',
              cache: true,
              success: function(d) {
                let tmp = this.state.vars;
                let max_filtered = moment(d["max_filtered"], "YYYY-MM-DD");
                let min_filtered = moment(d["min_filtered"], "YYYY-MM-DD");
                this.setState({dy_end: max_filtered.format("DD"), dy_start: min_filtered.format("DD"), mo_end: max_filtered.format("MM"), mo_start: min_filtered.format("MM"), yr_start: min_filtered.format("YYYY"), yr_end: max_filtered.format("YYYY"),f: e, mode: "docs", f_list: d["doclist"], f_counts: facet_datas[e]}, this.check_mode);
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
        });
  },

  qX: function(){
    if (this.state.f != -1){
      location.href='?q=' + this.state.f +'&corpus=' + this.props.corpus;
    }
  },

  fX: function(){
    let min;
    let max;
    min = moment(this.props.first_story_pubdate, "YYYY-MM-DD"); 
    max = moment(this.props.last_story_pubdate, "YYYY-MM-DD");
    this.setState({f: -1, mode:"overview", yr_start:min.format("YYYY"), mo_start:min.format("MM"), dy_start:min.format("DD"), yr_end:max.format("YYYY"), mo_end:max.format("MM"), dy_end:max.format("DD")});
  },

  render: function() {
    let f = this.state.f;
    let q = this.props.q;
    let qX = this.qX;
    let bin_size = "year"; //default binsize
    // docs = those that match q, f & t. all_results = what comes from browser.
    let docs = this.resultsToDocs(this.props.all_results);

    let y_scroll = {
        overflowY: "scroll",
        height:this.props.height
    };
    let binned_facets = _.sortBy(this.props.binned_facets, function(item) {
        return parseInt(item.key);
    });
    let yr_start = this.state.yr_start;
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

    let search_style = {
      fontWeight: "bold",
      color: "#0028a3"
    };

    let f_couts = this.state.f_counts;
    if (this.state.mode != "docs" & this.props.total_docs_for_q > 0){
      main_panel = <div>
                    <Status fX={this.fX} qX={qX} ndocs={this.props.total_docs_for_q} {...this.props}/>
                    <SparklineGrid {...this.props} clickTile={this.clickTile} q_data={q_data} col_no={3} width={this.props.width} facet_datas={this.props.facet_datas}/>
                   </div>
    } else { 
      main_panel = <DocViewer f={this.state.f} handleBinClick={this.handleBinClick} start_selected={this.state.start_selected} end_selected={this.state.end_selected} all_results={this.props.all_results} docs={docs} bin_size={bin_size} bins={binned_facets}/>
    }
    let chart;
    if (this.props.total_docs_for_q > 0){
      chart = <Chart qX={qX} set_date={this.set_date} start_selected={this.state.start_selected} end_selected={this.state.end_selected} {...this.props} f_data={f_couts} belowchart="50" height={this.props.width / this.props.w_h_ratio} width={this.props.width} keys={chart_bins} datas={q_data}/>
    }else{
      chart = "";
    }

    return(
        <div>
            <QueryBar corpus={this.props.corpus}/>
             <ChartTitle fX={this.fX} qX={qX} ndocs={this.props.total_docs_for_q} f={this.state.f} mode={this.state.mode} q={this.props.q} dy_start={this.state.dy_start} dy_end={this.state.dy_end} mo_start={this.state.mo_start} mo_end={this.state.mo_end} yr_start={this.state.yr_start} yr_end={this.state.yr_end}/>
             {chart}
            <div>
              {main_panel}
            </div>

       </div>);
  }
});