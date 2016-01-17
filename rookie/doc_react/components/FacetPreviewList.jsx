"use strict";
/*
FacetPreviewList
*/

var React = require('react');
var FacetPreview = require('./FacetPreview.jsx');

module.exports = React.createClass({
  getInitialState(){
    return {active: -1};
  },
  handleClick: function(item) {
    this.setState({active: item});
    this.props.handleBinClick(item);
  },
  render: function() {
    let fw = this.props.fontweight;
    let len_items = this.props.items.length;
    return (
      <span>
        {this.props.items.map(function(item, i) {
          let divStyle = {
              csolor: "black",
              fontsize: {fw},
              borderBottomColor: "grey"
          };
          return (
            <FacetPreview position={i} len_items={len_items} name={item} style={divStyle} onClick={this.handleClick} key={i}/>
          );
        }, this)}
      </span>
    );
  }
});
