import React from 'react';
import ReactDOM from 'react-dom';
import TemporalLinePlot from './App';

// Importing the Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

{/* width_to_height_ratio => lower # is a spikier, taller plot */}

ReactDOM.render(<TemporalLinePlot
                 x_axis_height={50} 
                 width_to_height_ratio={10}
                 q={"Q"}
                 q_data={q_data}
                 chart_bins={chart_bins}/>, document.getElementById('root'));
