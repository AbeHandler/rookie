'use strict';
/*
Question.jsx
*/

var React = require('react');
var ReactDOM = require('react-dom');
var Button = require('react-bootstrap/lib/Button');
var FormGroup = require('react-bootstrap/lib/FormGroup');
var Label = require('react-bootstrap/lib/Label');


/*

This API is so annoying. why these 2 
https://github.com/react-bootstrap/react-bootstrap/issues/1610*

*/
import {ControlLabel, FormControl, HelpBlock} from 'react-bootstrap';
var FormGroup = require('react-bootstrap/lib/FormGroup');

module.exports = React.createClass({

  getInitialState: function(){
    return {"picked": -1, "txt": ""}
  },

  change: function(e){
      this.setState({picked: e, txt: ReactDOM.findDOMNode(this.refs.input).value});
  },

  keychange: function(){
      this.setState({txt: ReactDOM.findDOMNode(this.refs.input).value});
  },

  check: function(){
      console.log(this.state.txt);
      console.log(this.state.txt.length);
      if (this.state.picked === -1){
        alert("please make a pick");
      }
      else if (this.state.txt.length < 25){
        alert("Please copy and paste a little bit more of the information you used to support this conclusion");
      }
      else {
        this.props.onsubmit(this.state.picked + "|||" + this.state.txt);
      }

  },

  getValidationState: function() {
    const length = this.state.txt.length;
    if (length > 25 && this.state.picked != -1) return 'success';
    else if (length > 0) return 'error';
  },

  render: function() {
    
    let width = this.props.width;
    let height = this.props.height;

    let tmp = this.change;
    let ans = this.props.answers;
      return (
              <div style={{width: "100%"}}>

              <div style={{width: "75%", margin: "auto"}}>
                    <div>
                    <FormGroup validationState={this.getValidationState()} controlId="formControlsTextarea">
                      <ControlLabel>Pick the best answer</ControlLabel>
                      {this.props.answers.map(function(k, v){
                        return (<div><input type="radio" name="1" value="1" onClick={() => tmp(v)}/><span style={{paddingLeft: "10px"}}> {k}</span> </div>)
                      })}
                      <ControlLabel>What information did you find to support this conclusion?</ControlLabel>
                      <FormControl onKeyDown={this.keychange} ref="input" componentClass="textarea" placeholder="Feel free to copy and paste" />
                      <FormControl.Feedback />
                     <HelpBlock>Validation is based on string length.</HelpBlock>
                    </FormGroup>
                    </div>

                    <Button onClick={this.check} bsStyle="primary">Submit</Button>
                </div>

              </div>


              )
    }
});
