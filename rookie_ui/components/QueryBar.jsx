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
    if (this.props.experiment_mode){
      alert("you dont need this feature for this task");
    }else{
      location.href= '/?q='+this.state.value + '&corpus=' + this.props.corpus;
    }
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
    let pstyle = {
      width:p_w,
      backgroundColor: "blue"
    }
    let submitter = this.submitter;
    let changeHandler = this.changeHandler;
    let sub_button;
    let col;
    if (this.props.experiment_mode){
      sub_button = "";
      col = 12;
    }else{
      sub_button = <Col xs={2} md={2}><Button onClick={submitter} type="submit">Submit</Button></Col>
      col = 10;
    }
    return (
      <Navbar style={{height:this.props.height, width: "100%"}} onKeyPress={(e)=> this.handleKeyPress(e)}>
        <Grid>
          <Row className="show-grid">
            <Col xs={col} md={col}><Input q={this.props.q} style={{pstyle}} changeHandler={changeHandler}/></Col>
            {sub_button}
          </Row>
        </Grid>
      </Navbar>
    )
  }

});