
  get_tooltip_q(){
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

      y_loc = this.props.height/5;
      //stop tooltip from extending past the edge of chart
      let pad_r = 50; //leeway
      if ((parseInt(this.props.tooltip_width) + x_scaled + this.props.y_axis_width + pad_r) > this.props.w){
        x_scaled = this.props.w - this.props.y_axis_width - pad_r - this.props.tooltip_width;
      }
      if (this.state.mouse_x == -1){
        opacity=0;
        tooltip_height=0; //hard to disable selection, so just put off screen
      }
      let tool_w = this.props.q.visualWidth();
      return <svg>
              <g>
              <rect x={x_scaled} rx="5" ry="5" y={y_loc} opacity={opacity} stroke="grey" strokeWidth="2" height={tooltip_height} width={tool_w + 110} fill="white"/>
              <text style={{backgroundColor: "white"}} x={x_scaled + 9} y={y_loc + 20} opacity={opacity} height="10" width="23" fill="black"><tspan style={{fontWeight: "bold"}}>{x_moment.format("MMM. YYYY")}</tspan>
              <tspan x={x_scaled + 9} y={y_loc + 40}>{nstories}</tspan><tspan> for</tspan>
              <tspan> </tspan><tspan style={{fontWeight: "bold", fill:"#0028a3"}}>{this.props.q}</tspan>
              </text>
              </g>
             </svg>
   }

    get_tooltip_q_and_f(){
      let x_loc = this.state.mouse_x;// - this.props.y_axis_width - this.props.buffer;
      let y_scale = this.get_y_scale();
      let x_scale = this.get_x_scale();
      let opacity=1;
      let x_date = x_scale.invert(x_loc - this.props.y_axis_width - this.props.buffer);
      let x_moment = moment(x_date);
      x_moment.startOf("month");
      let x_scaled = x_scale(x_moment);
      let y_loc = "";
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
      let nstories_ct = nstories;
      let fstories_ct = fstories;
      if (nstories > 1 || nstories == 0){
          nstories = nstories.toString() + " stories for ";
      }else if (nstories == 1){
          nstories = nstories.toString() + " story for ";
      }
      if (fstories > 1 || fstories == 0){
          fstories = fstories.toString() + " mention ";
      }else if (fstories == 1){
          fstories = fstories.toString() + " mention ";
      }
      let tooltip_height = 75;
      //if (y_loc > 20){  //stop tooltip from falling too low
      y_loc = 0;
      //}

      let tool_w = "";
      if (this.props.q.visualWidth() < this.props.f.visualWidth()){
        tool_w = this.props.f.visualWidth();
      }else{
        tool_w = this.props.q.visualWidth();
      }

      tool_w += 100; //padding

      if (nstories_ct >= 10){
        tool_w += 15; // "5 stories vs 15 stories... overflows tooltip"
      }

      //stop tooltip from extending past the edge of chart
      if ((tool_w + x_scaled) > this.props.w - this.props.y_axis_width - 5){
        x_scaled = this.props.w - this.props.y_axis_width - tool_w - 10;
      }
      if (this.state.mouse_x == -1){
        opacity=0;
        tooltip_height=0; //hard to disable selection, so just put off screen
      }
      
      
      return <svg>
              <g>
              <rect rx="5" ry="5" x={x_scaled} y={y_loc} opacity={opacity} stroke="grey" strokeWidth="2" height={tooltip_height} width={tool_w} fill="white"/>
              <text style={{backgroundColor: "white"}} x={x_scaled + 9} y={y_loc + 20} opacity={opacity} height="10" width="23" fill="black"><tspan style={{fontWeight: "bold"}}>{x_moment.format("MMM. YYYY")}</tspan>
              <tspan x={x_scaled + 9} y={y_loc + 40}>{nstories}</tspan><tspan style={{fontWeight: "bold", fill:"#0028a3"}}>{this.props.q}</tspan>
              <tspan x={x_scaled + 9} y={y_loc + 60}>{fstories}</tspan><tspan style={{fontWeight: "bold", fill:"#b33125"}}>{this.props.f}</tspan>
              </text>
              </g>
             </svg>
   }

   get_tooltip(){
      // no tooltip. important b.c otherwise ui does strange stuff w/ offscreen tooltip
      if (this.state.mouse_x == -1){
        return <svg></svg>;
      }
      if (this.props.f != -1){
        return <svg></svg>; // this.get_tooltip_q_and_f();
      }else{
        return <svg></svg>; //this.get_tooltip_q();
      }
   }