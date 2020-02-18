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

/*
var ChartTitle = require('./ChartTitle.jsx');
var SummaryStatus = require('./SummaryStatus.jsx');
var DocViewer = require('./DocViewer_generic.jsx');
var Modal_doc = require('./Modal_doc.jsx');
*/

import './App.css';

const App = () => (
  <div><QueryBar></QueryBar></div>
);

export default App;
