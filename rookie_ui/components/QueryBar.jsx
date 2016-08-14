/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Navbar = require('react-bootstrap/lib/Navbar');
var Button = require('react-bootstrap/lib/Button');
var Grid = require('react-bootstrap/lib/Grid');
var Row = require('react-bootstrap/lib/Row');
var Col = require('react-bootstrap/lib/Col');
var Input = require('./Input.jsx');

module.exports = React.createClass({

  submitter: function(){
    alert("You don't need this feature for this task");
  },

  getInitialState: function() {
    return {
      value: ''
    };
  },

  changeHandler: function(e) {

  },

  handleKeyPress: function(e){

  },

  render: function() {
    let dstyle = {
      width: "100%"
    }
    let p_w = $(document).width() * .8;
    let pstyle = {
      width:p_w,
      backgroundColor: "blue"
    }
    let submitter = this.submitter;
    let changeHandler = this.changeHandler;
    return (
      <Navbar style={{height:this.props.height, width: "100%"}}>
        <Grid>
          <Row className="show-grid">
            <Col xs={10} md={10}><Input q={this.props.q} style={{pstyle}} changeHandler={changeHandler}/></Col>
            <Col xs={2} md={2}><Button onClick={submitter} type="submit">Submit</Button></Col>
          </Row>
        </Grid>
      </Navbar>
    )
  }

});
