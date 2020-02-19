import React, { useState } from 'react';

import Jumbotron from 'react-bootstrap/Jumbotron';
import Toast from 'react-bootstrap/Toast';
import Container from 'react-bootstrap/Container';
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
  render() {return(<div>
                  <QueryBar></QueryBar><ChartTitle q={"Q"} f={-1} ndocs={5} fX={this.fX} requery={this.requery}></ChartTitle>
                  <Chart mouse_move_in_chart={this.mouse_move_in_chart.bind(this)} width={400} w={600} height={100} y_axis_width={55} q_data={q_data} f_data={f_counts} keys={chart_bins}></Chart>
                  </div>)}
}
