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
    return {"picked": -1, "txt": "", "txt2": ""}
  },

  change: function(e){
      this.setState({picked: e,
                    txt: ReactDOM.findDOMNode(this.refs.input).value,
                    txt2: ReactDOM.findDOMNode(this.refs.input2).value});
  },

  keychange: function(){
      this.setState({txt: ReactDOM.findDOMNode(this.refs.input).value,
                    txt2: ReactDOM.findDOMNode(this.refs.input2).value});
  },

  check: function(){
      this.setState({txt: ReactDOM.findDOMNode(this.refs.input).value}, function(){
        if (this.state.picked === -1){
          alert("please make a pick");
        }
        else if (this.state.txt.length < 25 || this.state.txt2.length < 25 ){
          console.log(this.state.txt.length, this.state.txt2.length);
          alert("Please copy and paste a little bit more of the information you used to support this conclusion");
        }
        else if (this.state.txt == this.state.txt2){
          alert("Please use two different sentences");
        }
        else {
          this.props.onsubmit(this.state.picked + "|||" + this.state.txt + "|||" + this.state.txt2);
        }
      });
  },

  getValidationState: function() {
    const length = this.state.txt.length;
    const length2 = this.state.txt2.length;
    if (length > 25 && length2 > 25 && this.state.picked != -1) return 'success';
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
                        return (<div><input type="radio" name="{k}" value="{k}" onClick={() => tmp(v)}/><span style={{paddingLeft: "10px"}}> {k}</span> </div>)
                      })}
                      <ControlLabel>Copy one sentence that supports your answer</ControlLabel>
                      <FormControl required={true} onChange={this.keychange} ref="input" componentClass="textarea" placeholder="Copy one sentence here" />
                      <ControlLabel>Copy a different sentence that supports your answer</ControlLabel>
                      <FormControl required={true} onChange={this.keychange} ref="input2" componentClass="textarea" placeholder="Copy a different sentence here" />
                    </FormGroup>
                    </div>

                     <Button onClick={this.check} bsStyle="primary">Submit</Button>

                </div>

              </div>


              )
    }
});
