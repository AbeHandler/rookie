'use strict';
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


  getInitialState: function() {
    let d1 = new Date(this.props.first_story_pubdate);
    let d2 = new Date(this.props.last_story_pubdate);
    let scale = this.get_x_scale();
    return {w: 0, x_l: scale(d1), x_r: scale(d2), drag_l: this.props.drag_l, drag_r: this.props.drag_r, mouse_to_r_d: -1, mouse_to_l_d: -1};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  set_X: function(e_pageX, lateral_scale) {
    let p = lateral_scale.invert(e_pageX - this.props.y_axis_width - this.props.buffer);
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
      console.log("aqui");
      this.props.set_date(p, "end");
    } else if (this.props.drag_l == true && this.props.drag_r == false){
      this.props.set_date(p, "start");
    }
  },

  /**
  * This function will fire when a user clicks the rectangle between the black bars
  */
  toggle_rect: function(){
    this.setState({drag_l : true, drag_r : true});
  },


  /**
  * This function will fire on mousedown
  * @param {Event} e 
  * @param {d3.scale} lateral_scale
  */
  handle_mouse_down: function(e, lateral_scale){
    if (this.props.chart_mode == "rectangle"){
      this.props.validClickTimer(e);
    }else{
      this.props.toggle_rect(lateral_scale.invert(e.pageX - this.props.y_axis_width - this.props.buffer), false);
    }
  },

  toggle_drag_start_l: function(){
    this.setState({drag_l : true});
  },

  toggle_drag_start_r: function(){
    this.setState({drag_r : true});
  },

  toggle_drag_stop: function(e, lateral_scale){
    this.setState({drag_l : false, mouse_to_r_d: -1, mouse_to_l_d: -1,
                   drag_r : false, mouse_to_r_d: -1, mouse_to_l_d: -1});
    this.props.validClickEnd(lateral_scale.invert(e));
  },
  
  render: function() {
    let lateralize = this.lateralize;
    let lateral_scale = this.get_x_scale();
    let height_scale = this.get_y_scale();
    let set_X = this.set_X;
    let ps = this.get_path_string(this.props.q_data);

    let fs = "";
    if (this.props.f_data.length > 0){
      fs = this.get_path_string(this.props.f_data);
    }
    let stroke_color_r = "black";
    if (this.props.drag_r == true){
      stroke_color_r = "red";
    }
    let stroke_color_l = "black";
    if (this.props.drag_l == true){
      stroke_color_l = "red";
    }
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
    let rec, l_left, l_right; 
    if (this.props.chart_mode == "rectangle"){
      rec = <rect onMouseDown={this.toggle_rect} y="0" x={start_pos} opacity={".2"} height={this.props.height} width={end_pos - start_pos} strokeWidth="4" fill="grey" />  
      l_left = <line onMouseDown={this.toggle_drag_start_l} x1={start_pos} y1={this.props.height / 4} x2={start_pos} y2={this.props.height * .75} stroke={stroke_color_l} strokeWidth="20"/>
      l_right = <line onMouseDown={this.toggle_drag_start_r} x1={end_pos} y1={this.props.height / 4} x2={end_pos} y2={this.props.height * .75} stroke={stroke_color_r} strokeWidth="20"/>
    }
    console.log(this.state);
    return (

        <Panel onMouseMove={e=> set_X(e.pageX, lateral_scale)} onMouseLeave={e=>this.toggle_drag_stop(e.pageX, lateral_scale)} onMouseUp={e =>  this.toggle_drag_stop(e.pageX, lateral_scale)} onMouseDown={e => this.handle_mouse_down(e, lateral_scale)} >
        <Row>
        <Col xs={12}>
        <YAxis max={max} height={this.props.height} y_axis_width={this.props.y_axis_width}/>
	      <svg width={this.props.w - this.props.y_axis_width - 5} height={this.props.height}>
        <path d={ps} fill="#0028a3" opacity=".25" stroke="grey"/>
        <path d={fs} fill="rgb(179, 49, 37)" opacity=".75" stroke="black"/>
        {rec}
        {l_left}
        {l_right}
        </svg>
        <div style={{width: this.props.y_axis_width - 2, float: "left"}}>&nbsp;</div><XAxis style={{float: "left"}} show_nth_tickmark="12" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={chart_width} q_counts={this.props.q_data} lateralize={lateralize}/>
        </Col>
        </Row>
        </Panel>
          
    );
  }
});
