"use strict";
/*
A list of linguistic facets. i.e. row of facet buttons
*/

var React = require('react');
var Name = require('./Name.jsx');

module.exports = React.createClass({
  handleClick: function(item) {
    this.props.onClick(item);
  },
  render: function() {
    return (<div>
        {this.props.items.map(function(item, i) {
          let selected = false;
          if (this.props.active===this.props.items[i].key){
              selected = true;
          }
          return (
            <Name selected={selected} data={item.data} name={item.key} onClick={this.handleClick} key={i}/>
          );
        }, this)}
      </div>);
  }
});