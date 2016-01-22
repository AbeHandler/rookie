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
  hoverCheck: function(item){
    return this.props.hovered===item;
  },
  handleHoverIn: function(item) {
    this.props.handleHoverIn(item);
  },
  handleHoverOut: function(item) {
    this.props.handleHoverOut(item);
  },
  render: function() {
    let fw = this.props.fontweight;
    let len_items = this.props.items.length;
    let hoverCheck = this.hoverCheck;
    let hoverIn = this.handleHoverIn;
    let hoverOut = this.handleHoverOut;
    return (
      <span>
        {this.props.items.map(function(item, i) {
          let divStyle = {
              csolor: "black",
              fontsize: {fw},
              borderBottomColor: "grey"
          };
          return (
            <FacetPreview handleHoverIn={hoverIn} handleHoverOut={hoverOut} isHovered={hoverCheck(item)} position={i} len_items={len_items} name={item} style={divStyle} onClick={this.handleClick} key={i}/>
          );
        }, this)}
      </span>
    );
  }
});
