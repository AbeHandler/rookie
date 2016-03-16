/*
Chart.jsx
*/

var React = require('react');
var ReactDOM = require('react-dom');
var d3 = require('d3');
var _ = require('lodash');
var moment = require('moment');
var YAxis = require('./YAxis.jsx');
var XAxis = require('./XAxis.jsx');

var Panel = require('react-bootstrap/lib/Panel');
var Row = require('react-bootstrap/lib/Row');
var Col = require('react-bootstrap/lib/Col');

module.exports = React.createClass({

  get_x_scale: function(){
      let str = new Date(_.first(this.props.keys));
      let end = new Date(_.last(this.props.keys));

      try{
          return d3.time.scale()
                            .domain([str, end])
                            .range([0, this.props.w - this.props.y_axis_width]);
      } catch(e){
          return d3.time.scale()
                            .domain([str, end])
                            .range([0, 0]); //has not loaded yet
      }

  },

    get_y_scale: function(){
      let h = this.props.w / this.props.w_h_ratio;
      return d3.scale.linear()
                            .domain([0, _.max(this.props.datas)])
                            .range([0, this.props.height])
    },

    get_path_string: function(input_datas){

        let bottom = this.props.height;
        let x_scale = this.get_x_scale();
        let y_scale = this.get_y_scale();

        let output = "M 0 " + bottom + " ";
        for (let i = 0; i < input_datas.length; i++) {
            let diff = this.props.height - parseFloat(y_scale(input_datas[i]));
            output = output + " L " + x_scale(new Date(this.props.keys[i])) + " " + diff;
        }
        output = output + "L " + x_scale(new Date(this.props.keys[input_datas.length - 1])) + " " + bottom;
        return output; // + "L 5 30 L 10 40 L 15 30 L 20 20 L 25 40 L 25 50 Z";
    },

    /**
    * Get the SVG path for the hightlight bar to show where mouseovered
    * @param {e_pageX} x location 
    * @param {lateral_scale} d3 scale
    */
    get_path_hilite: function(input_datas){

      let x_loc = this.state.mouse_x;// - this.props.y_axis_width - this.props.buffer;
      let y_scale = this.get_y_scale();
      let x_scale = this.get_x_scale();
      let opacity=1;
      if (this.state.mouse_x == -1){
        opacity=0;
      }
      let x_date = x_scale.invert(x_loc - this.props.y_axis_width - this.props.buffer);
      let x_moment = moment(x_date);
      x_moment.startOf("month");
      let x_scaled = x_scale(x_moment);
      let y_loc = this.props.height /2;
      let dates = _.map(this.props.keys, function(o, i){return moment(o)});
      let nstories = "";
      let j = 0;
      for (let i = 0; i < dates.length; i++) { 
          if(dates[i].year() == x_moment.year() && dates[i].month() == x_moment.month()){
              j = i;
          }
      }

      let bottom = this.props.height;
      let output = "";
      let diff = this.props.height - parseFloat(y_scale(input_datas[j]));
      output = "M " + x_scale(new Date(this.props.keys[j])) + " "  +  bottom + " ";
      output = output + " L " + x_scale(new Date(this.props.keys[j])) + " " + diff;
      output = output + "L " + x_scale(new Date(this.props.keys[j])) + " " + bottom;
      return output;
    },

  getInitialState: function() {
    let d1 = new Date(this.props.keys[0]);
    let d2 = new Date(this.props.keys[this.props.keys.length -1]);
    let scale = this.get_x_scale();
    let mouse_x = -1;
    let mouse_y = -1
    return {w: 0, mouse_x: mouse_x, x_l: scale(d1), x_r: scale(d2), 
           drag_l: this.props.drag_l, drag_r: this.props.drag_r, 
           mouse_to_r_d: -1, mouse_to_l_d: -1};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  handle_mouse_move: function(e_pageX, lateral_scale) {
    
    let p = lateral_scale.invert(e_pageX - this.props.y_axis_width - this.props.buffer);
    
    //alert UI that mouse is moving
    this.props.mouse_move_in_chart(p);

    if (this.props.drag_r == true && this.props.drag_l == true){
      //set distance from mouse position to edges  
      let lateral_scale = this.get_x_scale();
      let start_pos = lateral_scale(new Date(this.props.start_selected));
      let end_pos = lateral_scale(new Date(this.props.end_selected));
      if (this.state.mouse_to_r_d == -1 && this.state.mouse_to_l_d == -1){
        let rd = end_pos - e_pageX; //end position minus mouse position = right distance
        let ld = e_pageX - start_pos;
        this.setState({mouse_to_r_d: rd, mouse_to_l_d: ld});
      }
      this.props.set_dates(lateral_scale.invert(e_pageX - this.state.mouse_to_l_d), lateral_scale.invert(e_pageX + this.state.mouse_to_r_d));
    } else if (this.props.drag_r == true && this.props.drag_l == false){
      this.props.set_date(p, "end");
    } else if (this.props.drag_l == true && this.props.drag_r == false){
      this.props.set_date(p, "start");
    }
  },


  /**
  * This function will fire on mousedown
  * @param {Event} e 
  * @param {d3.scale} lateral_scale
  */
  handle_mouse_down: function(e, lateral_scale){
    if (this.props.chart_mode == "rectangle"){
      this.props.mouse_down_in_chart_true(lateral_scale.invert(e.pageX - this.props.y_axis_width - this.props.buffer));
    }else{
      this.props.toggle_rect(lateral_scale.invert(e.pageX - this.props.y_axis_width - this.props.buffer), false);
    }
  },

  toggle_drag_stop: function(e_pageX, lateral_scale){
    this.setState({ mouse_to_r_d: -1, mouse_to_l_d: -1,
                    mouse_to_r_d: -1, mouse_to_l_d: -1});
    this.props.mouse_up_in_chart(lateral_scale.invert(e_pageX - this.props.y_axis_width - this.props.buffer));
  },
  
  /**
  * This function will fire on mousedown
  * @param {e_pageX} x location 
  * @param {lateral_scale} d3 scale
  */
  handle_mouse_up_in_rect_mode: function(e_pageX, lateral_scale){
    this.setState({ mouse_to_r_d: -1, mouse_to_l_d: -1,
                    mouse_to_r_d: -1, mouse_to_l_d: -1});
    this.props.handle_mouse_up_in_rect_mode(e_pageX - this.props.y_axis_width - this.props.buffer, lateral_scale);
  },

  get_stroke_color_r: function(){
    let stroke_color_r = "black";
    if (this.props.drag_r == true){
      stroke_color_r = "red";
    }
    return stroke_color_r;
  },

  get_stroke_color_l: function(){
    let stroke_color_l = "black";
    if (this.props.drag_l == true){
      stroke_color_l = "red";
    }
    return stroke_color_l;
  },

  get_tooltip_q: function(){
      let x_loc = this.state.mouse_x;// - this.props.y_axis_width - this.props.buffer;
      let y_scale = this.get_y_scale();
      let x_scale = this.get_x_scale();
      let opacity=1;
      if (this.state.mouse_x == -1){
        opacity=0;
      }
      let x_date = x_scale.invert(x_loc - this.props.y_axis_width - this.props.buffer);
      let x_moment = moment(x_date);
      x_moment.startOf("month");
      let x_scaled = x_scale(x_moment);
      let y_loc = this.props.height /2;
      let dates = _.map(this.props.keys, function(o, i){return moment(o)});
      let nstories = "";
      for (let i = 0; i < dates.length; i++) { 
          if(dates[i].year() == x_moment.year() && dates[i].month() == x_moment.month()){
              let diff = this.props.height - parseFloat(y_scale(this.props.q_data[i]));
              y_loc = diff;
              nstories = this.props.q_data[i];
          }
      }
      if (nstories > 1){
          nstories = nstories.toString() + " stories";
      }else if (nstories == 1){
          nstories = nstories.toString() + " story";
      }else if (nstories == 0){
          nstories = nstories.toString() + " stories";
      }
      let tooltip_height = 50;
      if (y_loc > 50){  //stop tooltip from falling too low
        y_loc = 50; 
      }

      //stop tooltip from extending past the edge of chart
      if ((parseInt(this.props.tooltip_width) + x_scaled) > this.props.w - this.props.y_axis_width - 5){
        x_scaled = this.props.w - this.props.y_axis_width - 5 - this.props.tooltip_width - 5;
      }
      if (this.state.mouse_x == -1){
        opacity=0;
        tooltip_height=0; //hard to disable selection, so just put off screen
      }
      return <svg>
              <g>
              <rect x={x_scaled} rx="5" ry="5" y={y_loc} opacity={opacity} stroke="grey" strokeWidth="2" height={tooltip_height} width={this.props.tooltip_width} fill="white"/>
              <rect x={x_scaled + 5} y={y_loc + 30} height="10" width="10" opacity=".25" fill="#0028a3"/>
              <text style={{backgroundColor: "white"}} x={x_scaled + 9} y={y_loc + 20} opacity={opacity} height="10" width="23" fill="black"><tspan>{x_moment.format("MMM. YYYY")}</tspan><tspan x={x_scaled + 20} y={y_loc + 40}>{nstories}</tspan></text></g>
             </svg>
   },

    get_tooltip_q_and_f: function(){
      let x_loc = this.state.mouse_x;// - this.props.y_axis_width - this.props.buffer;
      let y_scale = this.get_y_scale();
      let x_scale = this.get_x_scale();
      let opacity=1;
      let x_date = x_scale.invert(x_loc - this.props.y_axis_width - this.props.buffer);
      let x_moment = moment(x_date);
      x_moment.startOf("month");
      let x_scaled = x_scale(x_moment);
      let y_loc = this.props.height /2;
      let dates = _.map(this.props.keys, function(o, i){return moment(o)});
      let nstories = "";
      let fstories = "";
      for (let i = 0; i < dates.length; i++) { 
          if(dates[i].year() == x_moment.year() && dates[i].month() == x_moment.month()){
              let diff = this.props.height - parseFloat(y_scale(this.props.q_data[i]));
              y_loc = diff;
              nstories = this.props.q_data[i];
              fstories = this.props.f_data[i];
          }
      }
      if (nstories > 1){
          nstories = nstories.toString() + " stories";
      }else if (nstories == 1){
          nstories = nstories.toString() + " story";
      }
      if (fstories > 1 || fstories == 0){
          fstories = fstories.toString() + " stories";
      }else if (fstories == 1){
          fstories = fstories.toString() + " story";
      }
      let tooltip_height = 75;
      if (y_loc > 50){  //stop tooltip from falling too low
        y_loc = 50; 
      }
      //stop tooltip from extending past the edge of chart
      if ((parseInt(this.props.tooltip_width) + x_scaled) > this.props.w - this.props.y_axis_width - 5){
        x_scaled = this.props.w - this.props.y_axis_width - 5 - this.props.tooltip_width - 5;
      }
      if (this.state.mouse_x == -1){
        opacity=0;
        tooltip_height=0; //hard to disable selection, so just put off screen
      }
      return <svg>
              <g>
              <rect rx="5" ry="5" x={x_scaled} y={y_loc} opacity={opacity} stroke="grey" strokeWidth="2" height={tooltip_height} width={this.props.tooltip_width} fill="white"/>
              <rect x={x_scaled + 5} y={y_loc + 30} height="10" width="10" opacity=".25" fill="#0028a3"/>
              <rect x={x_scaled + 5} y={y_loc + 50} height="10" width="10" opacity="1" fill="rgb(179, 49, 37)"/>
              <text style={{backgroundColor: "white"}} x={x_scaled + 9} y={y_loc + 20} opacity={opacity} height="10" width="23" fill="black"><tspan>{x_moment.format("MMM. YYYY")}</tspan>
              <tspan x={x_scaled + 20} y={y_loc + 40}>{nstories}</tspan>
              <tspan x={x_scaled + 20} y={y_loc + 60}>{fstories}</tspan>
              </text>
              </g>
             </svg>
   },

   get_tooltip: function(){
      // no tooltip. important b.c otherwise ui does strange stuff w/ offscreen tooltip
      if (this.state.mouse_x == -1){
        return <svg></svg>;
      }
      if (this.props.f != -1){
        return this.get_tooltip_q_and_f();
      }else{
        return this.get_tooltip_q();
      }
   },

  render: function() {
    let lateral_scale = this.get_x_scale();
    let height_scale = this.get_y_scale();
    let handle_mouse_move = this.handle_mouse_move;
    let ps = this.get_path_string(this.props.q_data);

    let fs = "";
    if (this.props.f_data.length > 0){
      fs = this.get_path_string(this.props.f_data);
    }
    let stroke_color_r = this.get_stroke_color_r();
    let stroke_color_l = this.get_stroke_color_l();
    let start_pos = lateral_scale(new Date(this.props.start_selected));
    let end_pos = lateral_scale(new Date(this.props.end_selected));
    if (start_pos < lateral_scale(_.first(this.props.keys))){
        start_pos = lateral_scale(_.first(this.props.keys));
    }
    if (end_pos > this.props.w){
        end_pos = lateral_scale(new Date(_.last(this.props.keys)));
    }
    let chart_width = this.props.w - this.props.y_axis_width - 5; 
    let max = _.max(this.props.datas);
    let rec, l_left, l_right, handle_mouseup; 
    if (this.props.chart_mode == "rectangle"){
      rec = <rect style={{cursor: "pointer"}} onMouseDown={this.props.toggle_both_drags_start} y="0" x={start_pos} opacity={".2"} height={this.props.height} width={end_pos - start_pos} strokeWidth="4" fill="grey" />  
      l_left = <line style={{cursor: "pointer"}} onMouseDown={this.props.toggle_drag_start_l} x1={start_pos} y1={this.props.height / 4} x2={start_pos} y2={this.props.height * .75} stroke={stroke_color_l} strokeWidth="20"/>
      l_right = <line style={{cursor: "pointer"}} onMouseDown={this.props.toggle_drag_start_r} x1={end_pos} y1={this.props.height / 4} x2={end_pos} y2={this.props.height * .75} stroke={stroke_color_r} strokeWidth="20"/>
    }
    if (this.props.drag_r == false && this.props.drag_l == false && this.props.chart_mode == "rectangle"){
      handle_mouseup = this.handle_mouse_up_in_rect_mode;
    }else{
      handle_mouseup = this.toggle_drag_stop;
    }
    let tooltip = this.get_tooltip();
    let hilite = this.get_path_hilite(this.props.q_data);
    return (
        <Panel onMouseMove={e=> handle_mouse_move(e.pageX, lateral_scale)} onMouseLeave={e=>this.toggle_drag_stop(e.pageX, lateral_scale)} onMouseUp={e => handle_mouseup(e.pageX, lateral_scale)} onMouseDown={e => this.handle_mouse_down(e, lateral_scale)} >
        <Row>
        <Col xs={12}>
        <YAxis max={max} height={this.props.height} y_axis_width={this.props.y_axis_width}/>
	      <svg ref="chart" width={this.props.w - this.props.y_axis_width - 5} height={this.props.height}>
        <path onMouseLeave={e=>this.setState({mouse_x:-1, mouse_y:-1})} onMouseMove={e =>this.setState({mouse_x:e.pageX})} d={ps} fill="#0028a3" opacity=".25" stroke="grey"/>
        <path d={hilite} fill="rgb(57, 57, 37)" opacity=".6" stroke="black"/>
        <path onMouseLeave={e=>this.setState({mouse_x:-1, mouse_y:-1})} onMouseMove={e =>this.setState({mouse_x:e.pageX})} d={fs} fill="rgb(179, 49, 37)" opacity=".6" stroke="black"/>
        {tooltip}
        {rec}
        {l_left}
        {l_right}
        </svg>
        <div style={{width: this.props.y_axis_width - 2, float: "left"}}>&nbsp;</div><XAxis style={{float: "left"}} show_nth_tickmark="12" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={chart_width} q_counts={this.props.q_data} lateralize={this.lateralize}/>
        </Col>
        </Row>
        </Panel>
          
    );
  }
});
