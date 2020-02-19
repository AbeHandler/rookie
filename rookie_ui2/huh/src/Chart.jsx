/*
Chart.jsx
*/

var React = require('react');
var ReactDOM = require('react-dom');
var d3 = require('d3');
var _ = require('lodash');
var moment = require('moment');

import XAxis from "./XAxis.jsx";
import YAxis from "./YAxis.jsx";

import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

export default class Chart extends React.Component{


  get_x_scale(){
      let str = new Date(_.first(this.props.keys));
      let end = new Date(_.last(this.props.keys));

      try{
          return d3.scaleTime()
                            .domain([str, end])
                            .range([0, this.state.width - this.props.y_axis_width]);
      } catch(e){
          return d3.scaleTime()
                            .domain([str, end])
                            .range([0, 0]); //has not loaded yet
      }

  }

    get_y_scale(){
      let h = this.props.w / this.props.w_h_ratio;
      return d3.scaleLinear()
                            .domain([0, _.max(this.props.q_data)])
                            .range([0, this.props.height])
    }

    get_path_string(input_datas, actual_plot_height){

        let bottom = actual_plot_height;
        let x_scale = this.get_x_scale();
        let y_scale = this.get_y_scale();

        let output = "M 0 " + bottom + " ";
        for (let i = 0; i < input_datas.length; i++) {
            let diff = actual_plot_height - parseFloat(y_scale(input_datas[i]));
            output = output + " L " + x_scale(new Date(this.props.keys[i])) + " " + diff;
        }
        output = output + "L " + x_scale(new Date(this.props.keys[input_datas.length - 1])) + " " + bottom;
        return output; // + "L 5 30 L 10 40 L 15 30 L 20 20 L 25 40 L 25 50 Z";
    }

    /**
    * Get the SVG path for the hightlight bar to show where mouseovered
    * @param {e_pageX} x location
    * @param {lateral_scale} d3 scale
    */
    get_path_hilite(input_datas){

      let x_loc = this.state.mouse_x;// - this.props.y_axis_width - this.props.buffer;
      let y_scale = this.get_y_scale();
      let x_scale = this.get_x_scale();
      let opacity=1;
      if (this.state.mouse_x == -1){
        opacity=0;
      }
      let x_date = this.mouse2date(x_loc);
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
    }

 constructor(props) {
    super(props);
    let d1 = new Date(this.props.keys[0]);
    let d2 = new Date(this.props.keys[this.props.keys.length -1]);
    let scale = this.get_x_scale();
    let mouse_x = -1;
    let mouse_y = -1;
    let panel_width = 0;
    this.myInput = React.createRef();
    this.state = {
            width: 0,
            panel_width: panel_width, 
            mouse_x: mouse_x,
            x_l: scale(d1),
            x_r: scale(d2),
            drag_l: this.props.drag_l,
            drag_r: this.props.drag_r,
            mouse_to_r_d: -1,
            mouse_to_l_d: -1
    };
  }

  lateralize(i, lateral_scale) {
    return lateral_scale(i);
  }

  handle_mouse_move(e_pageX) {

    let p = this.mouse2date(e_pageX)

    //alert UI that mouse is moving
    this.props.mouse_move_in_chart(p);

    if (this.props.drag_r == true && this.props.drag_l == true){
      //set distance from mouse position to edges
      let start_pos = this.start_date_x_position();
      let end_pos = this.end_date_x_position();
      if (this.state.mouse_to_r_d == -1 && this.state.mouse_to_l_d == -1){
        console.log("here");
        let mouse_date = this.mouse2date(e_pageX);

        let rd = end_pos // - e_pageX; //end position minus mouse position = right distance
        let ld = e_pageX  //- start_pos;
        this.setState({mouse_to_r_d: rd, mouse_to_l_d: ld});
      }
      this.props.set_dates(
                            this.mouse2date(e_pageX - this.state.mouse_to_l_d), 
                            this.mouse2date(e_pageX + this.state.mouse_to_r_d), 
                            this.mouse2date(e_pageX));
    } else if (this.props.drag_r == true && this.props.drag_l == false){
      this.props.set_date(p, "end");
    } else if (this.props.drag_l == true && this.props.drag_r == false){
      this.props.set_date(p, "start");
    }
  }


  mouse2date(x_loc){
     let x_loc_adjusted = x_loc - this.state.offset_left;
     let lateral_scale = this.get_x_scale();
     return lateral_scale.invert(x_loc_adjusted)
  }

  /**
  * This function will fire on mousedown
  * @param {Event} e
  * @param {d3.scale} lateral_scale
  */
  handle_mouse_down(e, lateral_scale){
    if (this.props.chart_mode == "rectangle"){
      this.props.mouse_down_in_chart_true(this.mouse2date(e.pageX));
    }else{
      this.props.turn_on_rect_mode(this.mouse2date(e.pageX));
    }
  }

  toggle_drag_stop(e_pageX){
    this.setState({ mouse_to_r_d: -1, mouse_to_l_d: -1,
                    mouse_to_r_d: -1, mouse_to_l_d: -1});
    this.props.mouse_up_in_chart(this.mouse2date(e_pageX));
  }

  get_stroke_color_r(){
    let stroke_color_r = "black";
    if (this.props.drag_r == true){
      stroke_color_r = "red";
    }
    return stroke_color_r;
  }

  get_stroke_color_l(){
    let stroke_color_l = "black";
    if (this.props.drag_l == true){
      stroke_color_l = "red";
    }
    return stroke_color_l;
  }

  turnoff_drag(){
    this.setState({ mouse_to_r_d: -1, mouse_to_l_d: -1, mouse_to_r_d: -1, mouse_to_l_d: -1}); 
    this.props.turnoff_drag();
  }

  componentDidMount() {
    const width = document.getElementById('chart_div').clientWidth;
    var offset_left = document.getElementById('main_chart').getBoundingClientRect().left;
    this.setState({"width": width,
                   "panel_width":width,
                   "offset_left":offset_left});
  }

  start_date_x_position(){
    let dt = new Date(this.props.start_selected);
    let x_scale = this.get_x_scale()

    let x_loc_adjusted = x_scale(dt);
    return x_loc_adjusted;
  }

  end_date_x_position(){
    let dt = new Date(this.props.end_selected);
    let x_scale = this.get_x_scale();

    let x_loc_adjusted = x_scale(dt);
    return x_loc_adjusted;
  }

  render() {

    {/* actual plot height is the height of the line plot itself rather than the height of the chart component which also includes x axis */}
    let actual_plot_height = this.props.height - this.props.x_axis_height

    {/* actual plot width is the width of the line plot itself rather than the width of the chart component which also includes y axis */}
    let actual_plot_width = this.state.width - this.props.y_axis_width

    let lateral_scale = this.get_x_scale();
    let height_scale = this.get_y_scale();
    let ps = this.get_path_string(this.props.q_data, actual_plot_height);

    let fs = "";
    if (this.props.f_data.length > 0){
      fs = this.get_path_string(this.props.f_data, actual_plot_height);
    }
    let stroke_color_r = this.get_stroke_color_r();
    let stroke_color_l = this.get_stroke_color_l();
    
    let start_pos =  this.start_date_x_position();
    let end_pos = this.end_date_x_position();

    let chart_width = this.props.w - this.props.y_axis_width - 5;

    if (start_pos < lateral_scale(_.first(this.props.keys))){
        start_pos = lateral_scale(_.first(this.props.keys));
    }
    if (end_pos > chart_width){
        end_pos = lateral_scale(new Date(_.last(this.props.keys)));
    }
   
    let max = _.max(this.props.q_data);
    let rec, l_left, l_right, handle_mouseup;
    if (this.props.chart_mode == "rectangle"){
      rec = <rect style={{cursor: "pointer"}} onMouseDown={this.props.toggle_both_drags_start} y="0" x={start_pos} opacity={".2"} height={this.props.height} width={end_pos - start_pos} strokeWidth="3" stroke="black" fill="grey" />
      l_left = <line style={{cursor: "col-resize"}} onMouseDown={this.props.toggle_drag_start_l} x1={start_pos} y1={this.props.height / 3} x2={start_pos} y2={this.props.height - (this.props.height / 3)} stroke={stroke_color_l} strokeWidth="6"/>
      l_right = <line style={{cursor: "col-resize"}} onMouseDown={this.props.toggle_drag_start_r} x1={end_pos} y1={this.props.height / 3} x2={end_pos} y2={this.props.height - (this.props.height / 3)} stroke={stroke_color_r} strokeWidth="6"/>
    }else{
      rec = "";
      l_left = "";
      l_right = ""
    }
    handle_mouseup = this.toggle_drag_stop.bind(this);
    {/* let tooltip = this.get_tooltip(); */}
    let tooltip  = "";
    let hilite = this.get_path_hilite(this.props.q_data);


    let yaxis = <YAxis max={max} height={actual_plot_height} y_axis_width={this.props.y_axis_width}/>

    let x_axis = <XAxis show_nth_tickmark="12" q={this.props.q} keys={this.props.keys} lateral_scale={lateral_scale} height="50" width={actual_plot_width} q_counts={this.props.q_data} lateralize={this.lateralize}/>

    let f_line = <path onMouseLeave={e=>this.setState({mouse_x:-1, mouse_y:-1})} onMouseMove={e =>this.setState({mouse_x:e.pageX})} d={fs} fill="rgb(179, 49, 37)" opacity=".6" stroke="black"/>

    let hilite_line = <path d={hilite} fill="rgb(57, 57, 37)" opacity=".6" stroke="black"/>

    let q_line = <path onMouseLeave={e=>this.setState({mouse_x:-1, mouse_y:-1})} onMouseMove={e =>this.setState({mouse_x:e.pageX})} d={ps} fill="#0028a3" opacity=".25" stroke="grey"/>

    
    let plot = <svg
            onMouseMove={e=> this.handle_mouse_move(e.pageX)}
            onMouseLeave={this.turnoff_drag.bind(this)}
            onMouseUp={e => handle_mouseup(e.pageX)}
            onMouseDown={e => this.handle_mouse_down(e, lateral_scale)}
            width={this.state.width - this.props.y_axis_width}
            height={actual_plot_height}>
            {q_line}
            {hilite_line}
            {f_line}
            {rec}
            {l_left}
            {l_right}
            </svg>
    return (
        <Card ref="chart_panel" style={{"width": "100%"}}>



        <div id="chart_div" style={{"width": "100%"}} ref={this.myInput}>

        {/*   y axis area */}
        <div style={{"width": this.props.y_axis_width, "height": this.props.height, float: "left"}}>

            {/*  the y-axis goes here */}
            <div style={{"width": "100%", "height": actual_plot_height}}> 
                {yaxis}
            </div>

            {/*  there is a little padding below where the x axis is */}
            <div style={{"width": "100%", "height":this.props.x_axis_height}}>
            
            </div>


        </div>

        {/*  x axis and main chart here */}
        <div style={{"width": this.state.width - this.props.y_axis_width, "height": this.props.height, float: "left"}}>

              {/*  main chart here */}
              <div id="main_chart" style={{"width": actual_plot_width, "height": this.props.height - this.props.x_axis_height}}>
                {plot}
              </div>

              {/*  X-axis here */}
              <div style={{"width": actual_plot_width, "height":this.props.x_axis_height}}>
              {x_axis}
              </div>

        </div>

        </div>

        </Card>

    );
  }
}
