/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Input = require('react-bootstrap/lib/Input');

module.exports = React.createClass({

getInitialState() {
    return {
      value: ''
    };
  },

  handleChange() {
    // This could also be done using ReactLink:
    // http://facebook.github.io/react/docs/two-way-binding-helpers.html
    this.setState({
      value: this.refs.input.getValue()
    });
    this.props.changeHandler(this.refs.input.getValue());
  },

  render() {
    return (
      <Input
        type="text"
        value={this.state.value}
        placeholder="Enter text"
        ref="input"
        groupClassName="group-class"
        labelClassName="label-class"
        onChange={this.handleChange} />
    );
  }

});