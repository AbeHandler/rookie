'use strict';
/*
Chart.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');
var moment = require('moment');

var Axis = require('./Axis.jsx');

module.exports = React.createClass({

    get_x_scale: function(){
      let str = new Date(_.first(this.props.keys));
      let end = new Date(_.last(this.props.keys));
      return d3.time.scale()
                            .domain([str, end])
                            .range([0, this.props.width]);
    },

    get_y_scale: function(){
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
    let x_l = scale(d1);
    let x_r = scale(d2);
    return {x_l: x_l, x_r: x_r, drag_l: false, drag_r: false, mouse_to_r_d: -1, mouse_to_l_d: -1};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  set_X: function(e_pageX, lateral_scale) {
    let p = lateral_scale.invert(e_pageX);
    if (this.state.drag_l == true && this.state.drag_r == false){
      this.props.set_date(p, "start");
    }
    if (this.state.drag_r == true && this.state.drag_l == false){
      this.props.set_date(p, "end");
    }
    if (this.state.drag_r == true && this.state.drag_r == true){
      //set distance from mouse position to edges
      console.log("i think measure the distance to edges on mouse down");
      console.log("then on move, maintain the edges as far away from mouse as when clicd");    
      let lateral_scale = this.get_x_scale();
      let start_pos = lateral_scale(new Date(this.props.start_selected));
      let end_pos = lateral_scale(new Date(this.props.end_selected));
      if (this.state.mouse_to_r_d == -1 && this.state.mouse_to_l_d == -1){
        let rd = end_pos - e_pageX; //end position minus mouse position = right distance
        let ld = e_pageX - start_pos;
        this.setState({mouse_to_r_d: rd, mouse_to_l_d: ld});
      }
      this.props.set_date(lateral_scale.invert(e_pageX + this.state.mouse_to_r_d), "end");
      this.props.set_date(lateral_scale.invert(e_pageX - this.state.mouse_to_l_d), "start");
    }
  },

  toggle_rect: function(e){
    this.setState({drag_l : true, drag_r : true});
  },

  toggle_drag_start: function(e){
    this.setState({drag_l : true});
  },

  toggle_drag_start_r: function(e){
    this.setState({drag_r : true});
  },

  toggle_drag_stop: function(e){
    this.setState({drag_l : false, mouse_to_r_d: -1, mouse_to_l_d: -1});
    this.setState({drag_r : false, mouse_to_r_d: -1, mouse_to_l_d: -1});
  },

  get_w: function(l, r){
    return r - l;
  },

  get_bar_width: function(){
    return this.props.width / this.props.datas.length;
  },

  render: function() {
    let lateralize = this.lateralize;
    let lateral_scale = this.get_x_scale();
    let height_scale = this.get_y_scale();
    let set_X = this.set_X;
    let f = this.props.f;
    let bar_width = this.get_bar_width();
    let ps = this.get_path_string(this.props.q_data);

    let x_l = lateral_scale(new Date(_.first(this.props.keys)));
    let x_r = lateral_scale(new Date(_.last(this.props.keys)));

    let fs = "";
    if (this.props.f_data.length > 0){
      fs = this.get_path_string(this.props.f_data);
    }
    let stroke_color_r = "black";
    if (this.state.drag_r == true){
      stroke_color_r = "red";
    }
    let stroke_color_l = "black";
    if (this.state.drag_l == true){
      stroke_color_l = "red";
    }
    let start_pos = lateral_scale(new Date(this.props.start_selected));
    let end_pos = lateral_scale(new Date(this.props.end_selected));
    if (start_pos < lateral_scale(_.first(this.props.keys))){
        start_pos = lateral_scale(_.first(this.props.keys));
    }
    if (end_pos > this.props.width){
        end_pos = lateral_scale(new Date(_.last(this.props.keys)));
    }
    return (

        <div onMouseMove={e=> set_X(e.pageX, lateral_scale)} onMouseLeave={this.toggle_drag_stop} onMouseUp={this.toggle_drag_stop}>
        <svg width={this.props.width} height={this.props.height}>
        <path d={ps} fill="#0028a3" opacity=".25" stroke="grey"/>
        <path d={fs} fill="rgb(179, 49, 37)" opacity=".75" stroke="black"/>

        <rect onMouseDown={this.toggle_rect} y="0" x={start_pos} opacity=".2" height={this.props.height} width={this.get_w(start_pos, end_pos)} strokeWidth="4" fill="grey" />  

        <line onMouseDown={this.toggle_drag_start} x1={start_pos} y1={this.props.height / 4} x2={start_pos} y2={this.props.height * .75} stroke={stroke_color_l} strokeWidth="20"/>
        <line onMouseDown={this.toggle_drag_start_r} x1={end_pos} y1={this.props.height / 4} x2={end_pos} y2={this.props.height * .75} stroke={stroke_color_r} strokeWidth="20"/>
        </svg>
        <Axis show_nth_tickmark="12" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={this.props.width} q_counts={this.props.q_data} lateralize={lateralize}/>
        </div>
          
    );
  }
});
