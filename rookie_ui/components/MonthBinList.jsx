/* jshint node: true */
"use strict";
var React = require('react');
var MonthBin = require('./MonthBin.jsx');

module.exports = React.createClass({

  is_selected: function (selected_mo, other_month){
    if (selected_mo == other_month){
        return true;
    }else{
        return false;
    }
  },

  render: function() {
    let months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    let rw_height = this.props.height / 12;
    let dStyle = {
        "height":rw_height,
        "cursor":"pointer",
        "borderBottom": "black",
        "borderBottomStyle": "solid",
        "borderBottomWidth": "1px",
        "marginBottom":"0"
    };

    if (this.props.selected === true){
        dStyle.backgroundColor = "rgba(102,126,199,.1)"; //same as region color
        dStyle.opacity = 1;
    }else{
        dStyle.opacity = .8;
    }

    let clicker = this.props.handleMo;
    let selected_mo = this.props.selected_mo;
    let is_selected = this.is_selected;
    return (
      <div>
        {months.map(function(item, i) {
          i++;

          return (
            <MonthBin selected_mo={is_selected(selected_mo, i)} monthNo={i} monthClick={clicker} style={dStyle} month={item} key={i}/>
          );
        })}
      </div>
    );
  }
});