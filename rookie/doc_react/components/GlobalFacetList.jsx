"use strict";
/*
A list of linguistic facets. i.e. row of facet buttons
*/

var React = require('react');
var GlobalFacetButton = require('./GlobalFacetButton.jsx');

module.exports = React.createClass({
  handleClick: function(item) {
    this.props.onClick(item);
  },
  handleHoverIn: function(item) {
    this.props.handleHoverIn(item);
  },
  handleHoverOut: function(item) {
    this.props.handleHoverOut(item);
  },
  hoverCheck: function(item){
    return this.props.hovered===item;
  },
  selectedCheck: function(item){
    return this.props.active===item;
  },
  render: function() {
    let hoverCheck = this.hoverCheck;
    let selectedCheck = this.selectedCheck;
    return (<div>
        {this.props.items.map(function(item, i) {
          //TODO: no logic in render
          let selected = selectedCheck(this.props.items[i]);
          let hovered = hoverCheck(this.props.items[i]);
          return (
            <GlobalFacetButton hovered={hovered} handleHoverOut={this.handleHoverOut} handleHoverIn={this.handleHoverIn} selected={selected} data={item.data} name={item} onClick={this.handleClick} key={i}/>
          );
        }, this)}
      </div>);
  }
});