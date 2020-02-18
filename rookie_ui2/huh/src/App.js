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
                   //start_selected: -1,
                   chart_mode: "intro",
                   end_selected: -1,
                   start_selected:min,
                   end_selected:max,
                   summary_page: 0,
                   f_counts: []});
  }
  requery(arg) {
      location.href= '/?q='+ arg + '&corpus=' + this.props.corpus;
  }
  render() {return(<div><QueryBar></QueryBar><ChartTitle ndocs={5} fX={this.fX} requery={this.requery}></ChartTitle></div>)}
}
