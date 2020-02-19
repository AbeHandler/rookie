import React, { useState } from 'react';

import Jumbotron from 'react-bootstrap/Jumbotron';
import Toast from 'react-bootstrap/Toast';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';

import Card from 'react-bootstrap/Card';

import Sparkline from "./Sparkline.jsx";
import QueryBar from "./QueryBar.jsx";
import SparklineGrid from "./SparklineGrid.jsx";

import Chart from './Chart.jsx';

import XAxis from "./XAxis.jsx";
import YAxis from "./YAxis.jsx";
import ClickableQF from "./ClickableQF.jsx"

import DocViewer from './DocViewer_generic.jsx'

import ChartTitle from './ChartTitle.jsx'

import SummaryStatus from './SummaryStatus.jsx'

import Modal_doc from './Modal_doc.jsx';

import './App.css';

var moment = require('moment');

export default class App extends React.Component{
  /**
  * A handler for when user clicks the X by F. Adjust state so f=-1
  */
  fX(){
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);

    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");

    this.setState({f: -1,
                   mode:"overview",
                   chart_mode: "intro",
                   end_selected: -1,
                   start_selected:min,
                   end_selected:max,
                   summary_page: 0,
                   f_counts: []});
  }

  turnoff_drag(){
    this.setState({drag_l: false, drag_r: false,
                   mouse_down_in_chart: false, summary_page: 0, mouse_is_dragging: false});
  }

  turn_on_rect_mode(p){
    this.setState({chart_mode:"rectangle",
                  start_selected:-1,
                  end_selected:-1,
                  mouse_down_in_chart:true,
                  summary_page: 0,
                  mode: "docs"});
  }

  constructor(props) {
    super(props);
    //Notes.
    //convention: -1 == null
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    this.state = {drag_r: false,
                 drag_l:false,
                 mouse_down_in_chart: false,
                 mouse_is_dragging: false,
                 width: 0,
                 height: 0,
                 click_tracker: -1,
                 chart_mode: "intro",
                 all_results: sents,
                 start_selected:min,
                 end_selected:max,
                 selected_doc: -1,
                 selectedheadline: "",
                 selectedsents: [],
                 selectedpubdate: "",
                 f_counts: this.props.f_counts,
                 f: this.props.f,
                 f_list: this.props.f_list,
                 summary_page: 0,
                 startdisplay: 0, //rank of first facet to display... i.e offset by?
                 kind_of_doc_list: "summary_baseline",
                 facet_datas: this.props.facet_datas,
                 mode: "docs"};
  }

  requery(arg) {
      location.href= '/?q='+ arg + '&corpus=' + this.props.corpus;
  }

  /**
  * This function will fire on mouseup if chart is in rectangle mode
  */
  mouse_up_in_chart(e_page_X_adjusted){
    if (this.state.start_selected == -1 && this.state.end_selected == -1){
      let s = moment(e_page_X_adjusted).add(-1, 'month');
      let e = moment(e_page_X_adjusted).add(1, 'month');
      s = s.format("YYYY-MM");
      e = e.format("YYYY-MM");

      this.setState({start_selected:s,end_selected:e, summary_page: 0});
    }else{
      let url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + this.state.start_selected + "&enddate=" + this.state.end_selected;

      let max = this.props.chart_bins[this.props.chart_bins.length - 1];


      if(this.state.start_selected === this.state.end_selected){
        if (moment(max) > moment(this.state.end_selected, "YYYY-MM")){
          let e = moment(this.state.end_selected, "YYYY-MM");
          e.add(1, "months");
          this.setState({end_selected:e.format("YYYY-MM"), summary_page: 0});
          url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + this.state.start_selected + "&enddate=" + e.format("YYYY-MM");
        }
      }

      if (this.state.f == -1){
        $.ajax({
                      url: url,
                      dataType: 'json',
                      cache: true,
                      method: 'GET',
                      success: function(d) {
                        //count vector for just clicked facet, e (event)
                        this.setState({facet_datas: d["d"], summary_page: 0, startdisplay:0});
                      }.bind(this),
                      error: function(xhr, status, err) {
                        console.error(this.props.url, status, err.toString());
                      }.bind(this)
        });
      }
    }

    this.setState({drag_l: false, drag_r: false,
                   mouse_down_in_chart: false, summary_page: 0, mouse_is_dragging: false});
  }

  /**
  * Set one of the dates: a start or end
  */
  set_date(date, start_end) {
    let d = moment(date);

    if (start_end == "start"){
      let end = moment(this.state.end_selected, "YYYY-MM");
      let min = moment(this.props.chart_bins[0]);
      if ((d < end) &  (d>min)){
        this.setState({start_selected:d.format("YYYY-MM"), summary_page: 0});
      }
    }
    if (start_end == "end"){
      let start = moment(this.state.start_selected, "YYYY-MM");

      let max = moment(this.props.chart_bins[this.props.chart_bins.length -1]);

      if (d > start & d < max){
         this.setState({end_selected:d.format("YYYY-MM"), summary_page: 0});
      }
    }
  }

  /**
  * The chart will now have drag_l is true
  */
  toggle_drag_start_l(){
    this.setState({drag_l : true, summary_page: 0, mouse_is_dragging: true});
  }

  /**
  * The chart will now have drag_r is true
  */
  toggle_drag_start_r(){
    this.setState({drag_r : true, summary_page: 0, mouse_is_dragging: true});
  }

  /**
  * This function will fire on mousedown if chart is in rectangle mode
  */
  mouse_down_in_chart_true(d){
    this.setState({
      mouse_down_in_chart: true,
      mouse_is_dragging: true}, function(){
        if (this.state.drag_l == false && this.state.drag_r == false){
          this.set_dates(d, d);
        }
      });
  }

  mouse_move_in_chart(p){
    if (this.state.mouse_down_in_chart){
      if (this.state.drag_l == false && this.state.drag_r == false){
        let start = moment(p).format("YYYY-MM");
        let end = moment(p).format("YYYY-MM");
        if (start === end)
        this.setState({mouse_is_dragging: true,
                      drag_l: false,
                      drag_r: true,
                      mode: "docs",
                      summary_page: 0,
                      start_selected: start,
                      end_selected: end});
      }
    }
  }

  /**
  * Set both dates at once: start and end
  */
  set_dates(start_date, end_date) {
    let s = moment(start_date);
    let e = moment(end_date);
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);


    if (s <= e  & s > min & e < max & !(s.format("YYYY-MM") === e.format("YYYY-MM"))) {
      let newstate = {start_selected:s.format("YYYY-MM"),
                     end_selected:e.format("YYYY-MM"),
                     summary_page: 0}
      this.setState(newstate);

    }else if (s <= e  & s > min & e < max & s.format("YYYY-MM") === e.format("YYYY-MM")){
        // dates are equal
        e.add(1, "months");
        let newstate = {start_selected:s.format("YYYY-MM"), end_selected:e.format("YYYY-MM"), summary_page: 0}
        if (e < max){
          this.setState({start_selected:s.format("YYYY-MM"),
                        end_selected:e.format("YYYY-MM"),
                        summary_page: 0});
        }
    }else{
      //console.log("skip");
    }
  }

  render() {
      let buffer = 5;
      let chart = <Chart
           tooltip_width="160"
           turn_on_rect_mode={this.turn_on_rect_mode.bind(this)}
           mouse_move_in_chart={this.mouse_move_in_chart}
           f={this.state.f}
           q={this.props.q}
           turnoff_drag={this.turnoff_drag.bind(this)}
           handle_mouse_up_in_rect_mode={this.handle_mouse_up_in_rect_mode}
           toggle_both_drags_start={() => this.setState({drag_l: true, summary_page: 0, drag_r: true}) }
           toggle_drag_start_l={this.toggle_drag_start_l.bind(this)}
           toggle_drag_start_r={this.toggle_drag_start_r.bind(this)}
           drag_l={this.state.drag_l}
           drag_r={this.state.drag_r}
           w={600}
           buffer={buffer}
           y_axis_width={55}
           mode={this.state.mode}
           mouse_move_in_chart={this.mouse_move_in_chart.bind(this)}
           mouse_up_in_chart={this.mouse_up_in_chart.bind(this)}
           mouse_down_in_chart_true={this.mouse_down_in_chart_true.bind(this)}
           chart_mode={this.state.chart_mode}
           qX={this.qX}
           set_date={this.set_date.bind(this)}
           set_dates={this.set_dates.bind(this)}
           start_selected={this.state.start_selected}
           end_selected={this.state.end_selected}
           q_data={this.props.q_data}
           f_data={f_counts}
           belowchart="50"
           height={200}
           x_axis_height = {50}
           keys={chart_bins}/>
    let debug = "mouse down=" + this.state.mouse_down_in_chart.toString();
    return(<div><Container>
                  <QueryBar></QueryBar><ChartTitle q={"Q"} f={-1} ndocs={5} fX={this.fX} requery={this.requery}></ChartTitle>
                  <Row>{chart}</Row>
                  </Container>{debug}</div>)}
}
