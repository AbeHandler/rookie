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

const App = () => (
  <div><QueryBar></QueryBar></div>
);

export default App;
