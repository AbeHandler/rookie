/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
import {ControlLabel, FormControl} from 'react-bootstrap';



module.exports = React.createClass({

getInitialState() {
    return {
      value: this.props.q
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
    let qstyle = {
      fontWeight: "bold",
      color: "#0028a3"
    };
    return (
      <FormControl
        type="text"
        style={qstyle}
        value={this.state.value}
        placeholder="Enter text"
        ref="input"
        groupClassName="group-class"
        labelClassName="label-class"
        onChange={this.handleChange} />
    );
  }

});
