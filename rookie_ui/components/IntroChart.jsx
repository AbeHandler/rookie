'use strict';
/*
Like chart, but w/ no rectangles.
Disappears on click.
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

  componentDidMount: function () {
     var width = ReactDOM.findDOMNode(this).offsetWidth - 30;
     this.setState({w: width});
  },

  get_x_scale: function(){
      let str = new Date(_.first(this.props.keys));
      let end = new Date(_.last(this.props.keys));
      try{
          return d3.time.scale()
                            .domain([str, end])
                            .range([0, this.state.w - this.props.y_axis_width]);
      } catch(e){
          return d3.time.scale()
                            .domain([str, end])
                            .range([0, 0]); //has not loaded yet
      }

  },

    get_y_scale: function(){
      let h = this.state.w / this.props.w_h_ratio;
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
    return {w: 0, x_l: x_l, x_r: x_r, drag_l: false, drag_r: false, mouse_to_r_d: -1, mouse_to_l_d: -1};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  report_click: function(e_pageX, lateral_scale) {
    let p = lateral_scale.invert(e_pageX);
    this.props.toggle_rect(p);
  },

  get_w: function(l, r){
    return r - l;
  },

  get_bar_width: function(){
    return this.state.w / this.props.datas.length;
  },

  render: function() {
    let lateralize = this.lateralize;
    let lateral_scale = this.get_x_scale();
    let height_scale = this.get_y_scale();
    let report_click = this.report_click;
    let f = this.props.f;
    let bar_width = this.get_bar_width();
    let ps = this.get_path_string(this.props.q_data);

    let x_l = lateral_scale(new Date(_.first(this.props.keys)));
    let x_r = lateral_scale(new Date(_.last(this.props.keys)));

    let fs = "";
    if (this.props.f_data.length > 0){
      fs = this.get_path_string(this.props.f_data);
    }

    let rc = this.report_click;
    let chart_width = this.state.w - this.props.y_axis_width - 5;
    let max = _.max(this.props.datas);
    return (

        <Panel onClick={e=> rc(e.pageX, lateral_scale)}>
        <Row>
        <Col xs={12}>
        <YAxis max={max} height={this.props.height} y_axis_width={this.props.y_axis_width}/>
	<svg width={chart_width} height={this.props.height}>
        <path d={ps} fill="#0028a3" opacity=".25" stroke="grey"/>
        <path d={fs} fill="rgb(179, 49, 37)" opacity=".75" stroke="black"/>
        </svg>
        <div style={{width: this.props.y_axis_width, float: "left"}}>&nbsp;</div><XAxis show_nth_tickmark="12" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={chart_width} q_counts={this.props.q_data} lateralize={lateralize}/>
        </Col>
        </Row>
        </Panel>
          
    );
  }
});
