"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');

var BinnedLinguisticFacets = require('./BinnedLinguisticFacets.jsx');
var LinguisticFacets = require('./LinguisticFacets.jsx');
var TemporalFacets = require('./TemporalFacets.jsx');
var DocViewer = require('./DocViewer.jsx');
var Chart = require('./Chart.jsx');

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

  handleF: function(e){
    //user just clicked an F button in LinguisticFacets
    if (this.state.f === e){
        this.setState({f: -1}, this.check_mode);
    }else{
        let url = "/post_for_docs?q=" + this.props.q + "&detail=" + e;
        $.ajax({
          url: url,
          dataType: 'json',
          cache: true,
          success: function(d) {
            this.setState({f: e, f_list: d}, this.check_mode);
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
        //TODO, what if T is selected?
    }
  },

  thiryDaysHath: function(e){
    if ([9, 11, 4, 5].indexOf(e)){
        return 30;
    } else if (e == 2){
        return 28;
    } else {
        return 30;
    }
  },

  handleMo:function (e){
    //the user just clicked a month facet, e
    let e1 = e + 1;
    this.setState({mo_start: e});
    this.setState({mo_end: e});
    this.setState({dy_start: 1});
    //thiry days hath september ... 
    //https://en.wikipedia.org/wiki/Thirty_days_hath_September#History
    //Since 1488!
    this.setState({dy_end: this.thiryDaysHath(e)});

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
    console.log(month);
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
    let min = this.get_min(this.props.all_results);
    let max = this.get_max(this.props.all_results);
    return {f: -1, yr_start:min.format("YYYY"), mo_start:min.format("MM"), dy_start:min.format("DD"), yr_end:max.format("YYYY"), mo_end:max.format("MM"), dy_end:max.format("DD"), mode:"overview"};
  },

  getStatus: function(ndocs){
    let status = "Found " + ndocs + " stories for " + this.props.q;
    if (this.state.mode == "overview"){
        status = status + " related to:";
    }else if (this.state.mode == "docs") {
        let start = moment(this.state.yr_start + "-" + this.state.mo_start + "-" + this.state.dy_start);
        let end = moment(this.state.yr_end + "-" + this.state.mo_end + "-" + this.state.dy_end);
        var duration = moment.duration(end.diff(start));
        if (this.state.f != -1){
            status = status + " and " + this.state.f; 
        }
        if (parseInt(this.state.dy_start) === 1 & parseInt(this.state.mo_start) === 1 & this.state.dy_end == "31" & this.state.mo_end == "12"){
            status = status + " in " + this.state.yr_start;
        }
        else if (Math.floor(duration.asDays()) < 32 & Math.floor(duration.asDays()) > 28){
            status = status + " in " + end.format("MMM YYYY");
        }else if (Math.floor(duration.asDays()) > 364 & Math.floor(duration.asDays()) < 366){
            status = status + " in " + start.format("YYYY");
        }
    }
    return status;
  },

  resultsToDocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list; 
    }
    let momentresults = _.map(results, function(n){
      return moment(n.pubdate);
    });
    let start = moment(this.state.mo_start + "-" + this.state.dy_start + "-" +  this.state.yr_start);
    let end = moment(this.state.mo_end + "-" + this.state.dy_end + "-" +  this.state.yr_end);
    return _.filter(results, function(value, key) {
        return moment(value.pubdate) >= start && moment(value.pubdate) <= end;
    });
  },

  render: function() {
    let f = this.state.f;
    let q = this.props.q;
    let bin_size = "year"; //default binsize
    // docs = those that match q, f & t. all_results = what comes from browser.
    let docs = this.resultsToDocs(this.props.all_results);
    let status = this.getStatus(docs.length);

    let y_scroll = {
        overflowY: "scroll",
        height:this.props.height
    };
    let binned_facets = _.sortBy(this.props.binned_facets, function(item) {
        return parseInt(item.key);
    });

    let row_height = Math.floor(this.props.height/binned_facets.length);

    let main_panel;

    let uiMonthHandler = this.handleMo;

    if (this.state.mode != "overview") {      
      main_panel = <div style={y_scroll}><DocViewer f={this.state.f} handleBinClick={this.handleBinClick} yr_start={this.state.yr_start} mo_start={this.state.mo_start} dy_start={this.state.dy_start} yr_end={this.state.yr_end} mo_end={this.state.mo_end} dy_end={this.state.dy_end} all_results={this.props.all_results} docs={docs} bin_size={bin_size} bins={binned_facets}/></div>;
    } else {
      //status = "Found " + this.props.all_results.length + " results for " + this.props.q + " related to:"
      main_panel = <BinnedLinguisticFacets rw_height={row_height} bin_size="year" handleMo={uiMonthHandler} handleBinDocsZoom={this.handleBinDocsZoom} f={f} handleF={this.handleF} bins={binned_facets}/>;
    }
    let rw = {
        width: "100%",
    };

    let start = moment(this.state.yr_start + "-" + this.state.mo_start + "-" + this.state.dy_start);
    let end = moment(this.state.yr_end + "-" + this.state.mo_end + "-" + this.state.dy_end);
    console.log("dddd");
    console.log(start.format("YYYY MM DD"));
    console.log(end.format("YYYY MM DD"));
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
    let rc = {
        width: (100 - left_col_width - 1).toString() + "%",
        float: "left",
        height: this.props.height
    };
    let handleMoUI = this.handleMo;
    return(
        <div>
            <div style={rw}>
                Subjects related to {q}:
            </div>
            <LinguisticFacets active={f} onClick={this.handleF} items={this.props.datas}/>
            <div>{status}</div>
            <div style={rw} >
                <div style={lc}><TemporalFacets vars={this.props.vars} q_data={this.props.q_data} bins={this.props.chart_bins} handleMo={handleMoUI} height={this.props.height} show_months={show_months} rw_height={row_height} yr_start={this.state.yr_start} mo_start={this.state.mo_start} dy_start={this.state.dy_start} yr_end={this.state.yr_end} mo_end={this.state.mo_end} dy_end={this.state.dy_end} handleBinClick={this.handleBinClick} docs={this.props.all_results} f={f} bin_size={bin_size}/></div>
                <div style={rc}>{main_panel}</div>
            </div>
            <div style={rw}>
            <Chart chart_bins={this.props.chart_bins} q_data={this.props.q_data} vars={this.props.vars} q={q} yr_start={this.state.yr_start} mo_start={this.state.mo_start} dy_start={this.state.dy_start} yr_end={this.state.yr_end} mo_end={this.state.mo_end} dy_end={this.state.dy_end} tHandler={this.handleT} f={this.state.f}/>
            </div>
       </div>);
  }
});