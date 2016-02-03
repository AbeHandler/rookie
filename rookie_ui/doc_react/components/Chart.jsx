'use strict';
/*
Chart.jsx
*/

var React = require('react');
var d3 = require('d3');
var _ = require('lodash');

var Axis = require('./Axis.jsx');
var Bar = require('./Bar.jsx');

module.exports = React.createClass({

    get_x_scale: function(){
      let str = new Date(this.props.keys[0]);
      let end = new Date(this.props.keys[this.props.keys.length-1]);
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
    let d1 = Date(this.props.yr_start, this.props.mo_start, this.props.dy_start);
    let d2 = Date(this.props.yr_end, this.props.mo_end, this.props.dy_end);
    let scale = this.get_x_scale();
    let x_l = scale(new Date(this.props.yr_start, this.props.mo_start, this.props.dy_start));
    let x_r = scale(new Date(this.props.yr_end, this.props.mo_end, this.props.dy_end));
    return {cache: {}, lscale: -1, x_l: x_l, x_r: x_r, y_r: 100, drag_l: false, drag_r: false};
  },

  lateralize: function (i, lateral_scale) {
    return lateral_scale(i);
  },

  set_X: function(e_pageX, lateral_scale) {
    let p;
    p = this.state.cache[e_pageX];
    if (p == undefined){
      p = lateral_scale(lateral_scale.invert(e_pageX));
      let tcache = this.state.cache;
      tcache[e_pageX] = p;
      this.setState({cache: tcache});
    }
    if (this.state.drag_l == true){
      this.setState({x_l: p});
    }
    if (this.state.drag_r == true){
      this.setState({x_r: p});
    }
  },

  get_height: function(i, scale){
    return scale(i);
  },

  get_y_offset: function(i, scale){
    let height = this.get_height(i, scale);
    return this.props.height - scale(i);
  },

  toggle_drag_start: function(e){
    this.setState({drag_l : true});
  },

  toggle_drag_start_r: function(e){
    this.setState({drag_r : true});
  },

  toggle_drag_stop: function(e){
    this.setState({drag_l : false});
    this.setState({drag_r : false});
  },

  get_w: function(l, r){
    return r - l;
  },

  get_key: function(i, r){
    let keystring = i + r;
    return keystring;
  },

  get_bar_width: function(){
    return this.props.width / this.props.datas.length;
  },

  render: function() {
    let min = _.min(this.props.q_counts);
    let max = _.max(this.props.q_counts);
    let height = this.props.height;
    let width = this.props.width;
    let lateralize = this.lateralize;
    let get_height = this.get_height;
    let get_y_offset = this.get_y_offset;
    let lateral_scale = this.get_x_scale();
    let height_scale = this.get_y_scale();
    let xAxis = d3.svg.axis()
                   .scale(height_scale);
    let cliq = this.handleclick;
    let set_X = this.set_X;
    let get_key = this.get_key;
    let q = this.props.q;
    let f = this.props.f;
    let bar_width = this.get_bar_width();
    let ps = this.get_path_string(this.props.q_data);
    let fs = "";
    if (this.props.f_data.length > 0){
      fs = this.get_path_string(this.props.f_data);
    }
    return (

        <div onMouseMove={e=> set_X(e.pageX, lateral_scale)} onMouseLeave={this.toggle_drag_stop} onMouseUp={this.toggle_drag_stop}>
        <svg width={this.props.width} height={this.props.height}>
        <path d={ps} fill="#0028a3" opacity=".25" stroke="grey"/>
        <path d={fs} fill="rgb(179, 49, 37)" opacity=".75" stroke="black"/>
        {/* background for chart */}
        {/* ->that crazy looking lambda invert scales the X position, takes the floor and then scales it again.
            ->the point of doing that is to limit the possible range of x positions. so x gets mapped to only one of 
            n locations, where n = the number of datapoints. 
          */}
        <rect y="0" x={this.state.x_l} opacity=".2" height={this.props.height} width={this.get_w(this.state.x_l, this.state.x_r)} strokeWidth="4" fill="grey" />  

        {/*
        {this.props.q_counts.map(function(value, i){
             return <Bar set_X={set_X} width={bar_width} q={q} f={f} key={get_key("q", i)} color="blue" get_height={get_height} height_scale={height_scale} value={value} i={i} lateral_scale={lateral_scale} lateralize={lateralize} get_y_offset={get_y_offset}/>
          })
        }*/}

        {/*
        {this.props.f_counts.map(function(value, i){
            return <Bar width={bar_width} q={q} f={f} key={get_key("f", i)} type="f" color="red" get_height={get_height} height_scale={height_scale} value={value} i={i} set_X={set_X} lateral_scale={lateral_scale} lateralize={lateralize} get_y_offset={get_y_offset}/>
        })}
        */}

        <line onMouseDown={this.toggle_drag_start} x1={this.state.x_l} y1={this.props.height / 4} x2={this.state.x_l} y2={this.props.height * .75} stroke="black" strokeWidth="10"/>
        <line onMouseDown={this.toggle_drag_start_r} x1={this.state.x_r} y1={this.props.height / 4} x2={this.state.x_r} y2={this.props.height * .75} stroke="black" strokeWidth="10"/>
        </svg>
        <Axis show_nth_tickmark="24" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={this.props.width} q_counts={this.props.q_data} lateralize={lateralize}/>
        </div>
          
    );
  }
});
