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


module.exports = React.createClass({

  check_mode: function(){
    if (this.state.f != -1){
        this.setState({mode: "docs"});
    }else{
        //f is not selected
        if (this.t_not_selected()){
            this.setState({mode: "overview"});
        }else{
            this.setState({mode: "docs"});
        }
    }
  },
  
  t_not_selected: function(){
    let min = this.get_min(this.props.all_results);
    let max = this.get_max(this.props.all_results);
    let t_start = moment(this.state.yr_start + "-" + this.state.mo_start + "-" + this.state.dy_start);
    let t_end = moment(this.state.yr_end + "-" + this.state.mo_end + "-" + this.state.dy_end);
    if (min.format("MM-DD-YYY") == t_start.format("MM-DD-YYY") & max.format("MM-DD-YYY") == t_end.format("MM-DD-YYY")){
        return true;
    }
    return false;
  },

  thiryDaysHath: function(e){
    if (_.includes([9, 11, 4, 6], e)){
        return 30;
    } else if (e == 2){
        return 28;
    } else {
        return 31;
    }
  },

  handleMo:function (e){
    //the user just clicked a month facet, e

    //if the month is already selected... unselect it
    if (this.state.mo_start == e && this.state.mo_end == e){
      this.setState({mo_start: 1});
      this.setState({mo_end: 12});
      this.setState({dy_start: 1});
      this.setState({dy_end: 31});
    }else{
      this.setState({mo_start: e});
      this.setState({mo_end: e});
      this.setState({dy_start: 1});
      //thiry days hath september ... 
      //https://en.wikipedia.org/wiki/Thirty_days_hath_September#History
      //Since 1488!
      this.setState({dy_end: this.thiryDaysHath(e)});      
    }
  },


  handleBinClick: function(e){
    //user just clicked a TFacet
    //TODO: assuming bin year here.
    if (this.state.yr_start == parseInt(e) & this.state.yr_end == parseInt(e)){
        let min = this.get_min(this.props.all_results);
        let max = this.get_max(this.props.all_results);
        this.setState({yr_start: min.format("YYYY"), mo_start:min.format("MM"), dy_start:min.format("DD"), yr_end: max.format("YYYY"), mo_end:max.format("MM"), dy_end:max.format("DD")}, this.check_mode);
    }else{
        this.setState({yr_start: e, mo_start:"01", dy_start:"01", yr_end: e, mo_end:"12", dy_end:"31"}, this.check_mode);
    }
    this.check_mode();
  },

  handleT: function(e){
    let year = e.x.getFullYear();
    let month = e.x.getMonth() + 1;
    let day = e.x.getDay();
    this.setState({yr_start: year, mo_start:month, dy_start:1, yr_end: year, mo_end:month, dy_end:this.thiryDaysHath(month)}, this.check_mode);
  },

  handleBinDocsZoom: function(e, zoom_level){
    if (zoom_level == "year"){
        this.setState({yr_start: e, mo_start:"01", dy_start:"1", yr_end: e, mo_end:"12", dy_end:"31"}, this.check_mode);
    }
  },

  get_min: function(results){
    let momentresults = _.map(results, function(n){
      return moment(n.pubdate);
    });
    return _.min(momentresults);
  },

  get_max: function(results){
    let momentresults = _.map(results, function(n){
      return moment(n.pubdate);
    });
    return _.max(momentresults);
  },

  show_month_bins: function(start, end){
    if (end.diff(start, 'days') < 366){
        return true;
    }else{
        return false;
    }
  },

  getInitialState(){
    //Notes.
    //1) convention: -1 == null
    //2) keeping track of y/mo/dy is annoying but react won't allow object as prop
    //3) there can be exactly 1 linguistic facet from a bin (as opposed to global) that is
    //   promoted up to global at one time. stored in state.promoted_l_facet
    let min;
    let max;
    if (this.props.all_results.length > 0){
        min = this.get_min(this.props.all_results);
        max = this.get_max(this.props.all_results);      
    } else{
        min = moment("01-01-2010"); //TODO: hardcoded for Lens corpus
        max = moment("05-01-2010", "MM-DD-YYYY"); //TODO: hardcoded for Lens corpus
    }
    //TODO: if no results, this fails
    return {f_counts:[], f: -1, hovered: -1, vars:this.props.vars, yr_start:min.format("YYYY"), mo_start:min.format("MM"), dy_start:min.format("DD"), yr_end:max.format("YYYY"), mo_end:max.format("MM"), dy_end:max.format("DD"), mode:"overview", promoted_l_facet: -1};
  },

  linguisticFacetHoverIn: function(e){
    this.setState({hovered: e});
  },

  linguisticFacetHoverOut: function(e){
    this.setState({hovered: -1});
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

  handleLinguisticFacetClick: function(e){
    if (this.state.f === e){
        this.setState({f: -1}, this.check_mode);
    } else{
      let url = "/get_docs?q=" + this.props.q + "&f=" + e + "&corpus=" + this.props.corpus;
        $.ajax({
              url: url,
              dataType: 'json',
              cache: true,
              success: function(d) {
                let tmp = this.state.vars;
                this.setState({f_counts: d["facet_datas"][e], promoted_l_facet: e, f: e, f_list: d["doclist"]}, this.check_mode);
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
        });
     } 
  },

  get_global_facets: function(){
    let tmp = this.props.datas; //fixed global facets
    if (this.state.promoted_l_facet != -1 & !_.includes(this.props.datas, this.state.promoted_l_facet)){
      tmp.push(this.state.promoted_l_facet);
    }
    return tmp;
  },

  getDuration: function(){
    let start = moment(this.state.yr_start + "-" + this.state.mo_start + "-" + this.state.dy_start);
    let end = moment(this.state.yr_end + "-" + this.state.mo_end + "-" + this.state.dy_end);
    var duration = moment.duration(end.diff(start));
    return duration;
  },

  render: function() {
    let f = this.state.f;
    let q = this.props.q;
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
    let duration = this.getDuration();
    //TODO: this is logic-y and should not go in render
    if (this.state.yr_start == this.state.yr_end && this.state.mo_end == 12 && this.state.mo_start == 1 && this.state.f == -1){
      selected_binned_facets = _.filter(binned_facets, function(o) { 
        return o.key == yr_start;
      });
    }else if(duration.days() < 360){
        selected_binned_facets = [];
    }else{
      selected_binned_facets = binned_facets;
    }

    let row_height = Math.floor(this.props.height/binned_facets.length);

    let main_panel;

    let uiMonthHandler = this.handleMo;
    let b_f_click = this.handleLinguisticFacetClick;
    if (this.state.mode != "overview") {      
      main_panel = <div style={y_scroll}>
                    <BinnedLinguisticFacets hovered={this.state.hovered} handleHoverOut={this.linguisticFacetHoverOut} handleHoverIn={this.linguisticFacetHoverIn} hovered={this.state.hovered} bin_size="year" handleMo={uiMonthHandler} f={f} handleBinClick={b_f_click} bins={selected_binned_facets}/>
                    <DocViewer f={this.state.f} handleBinClick={this.handleBinClick} yr_start={this.state.yr_start} mo_start={this.state.mo_start} dy_start={this.state.dy_start} yr_end={this.state.yr_end} mo_end={this.state.mo_end} dy_end={this.state.dy_end} all_results={this.props.all_results} docs={docs} bin_size={bin_size} bins={binned_facets}/>
                   </div>;
    } else if (docs.length == 0){
      main_panel = <div></div>;
    } else {
      //status = "Found " + this.props.all_results.length + " results for " + this.props.q + " related to:"
      main_panel = <BinnedLinguisticFacets hovered={this.state.hovered} handleHoverOut={this.linguisticFacetHoverOut} handleHoverIn={this.linguisticFacetHoverIn} hovered={this.state.hovered} rw_height={row_height} bin_size="year" handleMo={uiMonthHandler} handleBinClick={b_f_click} handleBinDocsZoom={this.handleBinDocsZoom} f={f} handleF={this.handleF} bins={binned_facets}/>;
    }
    let rw = {
        width: "100%",
    };

    let start = moment(this.state.yr_start + "-" + this.state.mo_start + "-" + this.state.dy_start);
    let end = moment(this.state.yr_end + "-" + this.state.mo_end + "-" + this.state.dy_end);
    let show_months = this.show_month_bins(start, end);
    let left_col_width = 10;
    let lc = {
        width: left_col_width.toString() + "%",
        borderRight: "1px solid gray",
        marginRight:"1%",
        float: "left",
        height: this.props.height,
        textAlign: "center"
    };
    if (docs.length == 0){
      lc.borderRight = "1px solid white"
    };
    let rc = {
        width: (100 - left_col_width - 1).toString() + "%",
        float: "left",
        height: this.props.height
    };
    let handleMoUI = this.handleMo;
    let items = this.get_global_facets();

    var binned_counts_f = this.props.binned_counts_f;

    let chart_bins = this.props.chart_bins;

    let search_style = {
      fontWeight: "bold",
      color: "#0028a3"
    };
    let f_couts = this.state.f_counts;

    return(
        <div>
            
            <div id="controls" className="row">
              <div>
                <div className="small-10 columns">
                  <input onChange={handleMoUI} style={search_style} type="text" value={this.props.q} placeholder={this.props.q}></input>
                </div>
                <div className="small-2 columns">
                  <a href="#" className="button postfix" id="search_button">Search</a>
                </div>
              </div>

            </div>
             <ChartTitle ndocs={this.props.total_docs_for_q} f={this.state.f} mode={this.state.mode} q={this.props.q} dy_start={this.state.dy_start} dy_end={this.state.dy_end} mo_start={this.state.mo_start} mo_end={this.state.mo_end} yr_start={this.state.yr_start} yr_end={this.state.yr_end}/>
             <Chart f_counts={f_couts} q={this.props.q} f={this.state.f} show_nth_tickmark="12" belowchart="50" height="150" width={this.props.width} keys={chart_bins} q_counts={q_data}/>

             <Status  {...this.props}/>
            <div>
            <SparklineGrid col_no={3} width={this.props.width} tileheight={50} facet_datas={this.props.facet_datas}/>
            </div>

            {/*
            <div style={rw} >
                <div style={lc}><TemporalFacets n_results={this.props.all_results.length} f_counts={this.state.f_counts} q_data={this.props.q_data} bins={this.props.chart_bins} handleMo={handleMoUI} height={this.props.height} show_months={show_months} rw_height={row_height} yr_start={this.state.yr_start} mo_start={this.state.mo_start} dy_start={this.state.dy_start} yr_end={this.state.yr_end} mo_end={this.state.mo_end} dy_end={this.state.dy_end} handleBinClick={this.handleBinClick} docs={this.props.all_results} f={f} bin_size={bin_size}/></div>
                <div style={rc}>{main_panel}</div>
            </div>
            <div style={rw}>
            </div>
            */}
       </div>);
  }
});