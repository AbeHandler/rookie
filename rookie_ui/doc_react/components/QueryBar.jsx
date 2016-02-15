/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Navbar = require('react-bootstrap/lib/Navbar');
var Button = require('react-bootstrap/lib/Button');
var Input = require('./Input.jsx');

module.exports = React.createClass({

  submitter: function(){
    location.href= '?q='+this.state.value + '&corpus=' + this.props.corpus;
  },

  getInitialState: function() {
    return {
      value: ''
    };
  },

  changeHandler: function(e) {
    this.setState({
      value: e
    });
  },

  handleKeyPress: function(e){
    if (e.which == 13){ //enter key
      this.submitter();
    }
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
    let submitter = this.submitter;
    let changeHandler = this.changeHandler;
    return (
      <Navbar onKeyPress={(e)=> this.handleKeyPress(e)}>
          <Navbar.Collapse>
            <Navbar.Form pullLeft style={qstyle}>
              <Input changeHandler={changeHandler}/>
              <Button onClick={submitter} type="submit">Submit</Button>
            </Navbar.Form>
          </Navbar.Collapse>
        </Navbar>
    )
  }

});