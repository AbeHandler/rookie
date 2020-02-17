/* jshint node: true */
/* A list of days */
"use strict";
var React = require('react');
var $ = require('jQuery');
var Navbar = require('react-bootstrap/Navbar');
var Button = require('react-bootstrap/Button');
var Container = require('react-bootstrap/Container');
var Row = require('react-bootstrap/Row');
var Col = require('react-bootstrap/Col');

var Input = require('./Input.jsx');

export default class QueryBar extends React.Component {

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
 }


  changeHandler(e) {
    this.setState({
      value: e
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
        <Container>
          <Row className="show-grid">
            <Col xs={col} md={col}><Input q={this.props.q} style={{width:p_w, backgroundColor: "blue"}} changeHandler={changeHandler}/></Col>
            {sub_button}
          </Row>
        </Container>
      </Navbar>
    )
  }

}
