import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

// Importing the Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

ReactDOM.render(<App q={"Q"} q_data={q_data} chart_bins={chart_bins}/>, document.getElementById('root'));
