/* jshint node: true */
/* A list of days */
"use strict";
import React from 'react';

var $ = require('jquery');

import Navbar from 'react-bootstrap/Navbar';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import Input from './Input.jsx';

import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';

export default class QueryBar extends React.Component{

  submitter(){
    if (this.props.experiment_mode){
      alert("you dont need this feature for this task");
    }else{
      location.href= '/' + this.props.url_method + '?q='+this.state.value + '&corpus=' + this.props.corpus;
    }
  }

 constructor(props) {
    super(props);
    this.state = {value: this.props.q}
    this.changeHandler = this.changeHandler.bind(this);
 }


  changeHandler(e) {
    this.setState({
      value: e.target.value
    });
  }

  handleKeyPress(e){
    if (e.which == 13){ //enter key
      this.submitter();
    }
  }

  render() {
    let p_w = $(document).width() * .8;
    let submitter = this.submitter;
    let sub_button;
    let col;
    if (this.props.experiment_mode){
      sub_button = "";
      col = 12;
    }else{
      sub_button = <Col xs={2} md={2}><Button onClick={submitter} type="submit">Submit</Button></Col>
      col = 10;
    }
    var v = this.state.value;
    return (<Navbar style={{height:this.props.height, width: "100%"}} onKeyPress={(e)=> this.handleKeyPress(e)}>
        <Container>
          <Row className="show-grid">
            <Col xs={col} md={col}>
                <InputGroup size="lg">
                  <FormControl onChange={this.changeHandler} aria-label="Large" aria-describedby="inputGroup-sizing-sm" />
                </InputGroup>
            </Col>
            {sub_button}
          </Row>
        </Container>
      </Navbar>
    )
  }

}
