/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Navbar = require('react-bootstrap/lib/Navbar');
var Input = require('react-bootstrap/lib/Input');
var Button = require('react-bootstrap/lib/Button');

module.exports = React.createClass({

  pop: function(e){
    alert(e);
  },

  getInitialState: function() {
    return {
      value: ''
    };
  },


  handleChange: function() {
    // This could also be done using ReactLink:
    // http://facebook.github.io/react/docs/two-way-binding-helpers.html
    console.log(this.refs.input.getValue());
    this.setState({
      value: this.refs.input.getValue()
    });
  },


  render: function() {
    let demo = "one";
    let demo2 = "two";
    let dstyle = {
      width: "100%"
    }
    let p_w = $(document).width() * .8;
    let qstyle = {
      width: "100%"
    }
    let pstyle = {
      width:p_w
    }
    let onClicker = this.pop;;
    return (
      <Navbar>
          <Navbar.Collapse>
            <Navbar.Form pullLeft style={qstyle}>
              <Input hasFeedback handleChange={this.handleChange} value={this.state.value} style={pstyle} type="text" placeholder="Search"/>
              {' '}
              <Button type="submit">Submit</Button>
            </Navbar.Form>
          </Navbar.Collapse>
        </Navbar>
    )
  }

});