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
import {ControlLabel, FormControl} from 'react-bootstrap';
var FormGroup = require('react-bootstrap/lib/FormGroup');

module.exports = React.createClass({

  getInitialState: function(){
    return {"picked": -1}
  },

  change: function(e){
      this.setState({picked: e, txt: this.refs.input.getValue()});
  },



  render: function() {
    
    let width = this.props.width;
    let height = this.props.height;

    let tmp = this.change;
    let ans = this.props.answers;
      return (
              <div style={{width: "100%"}}>

              <div style={{width: "75%", margin: "auto"}}>
                    <div style={{fontWeight: "bold"}}>Pick the best answer</div>
                    {this.props.answers.map(function(k, v){
                      return (<div><input type="radio" name="1" value="1" onClick={() => tmp(v)}/><span style={{paddingLeft: "10px"}}> {k}</span> </div>)
                    })}
                    
                    <p/>
                    <div style={{fontWeight: "bold"}}>What information did you find to support this conclusion?</div>
                    <div>
                    <FormGroup controlId="formControlsTextarea">
                      <ControlLabel>Textarea</ControlLabel>
                      <FormControl componentClass="textarea" placeholder="textarea" />
                    </FormGroup>
                    </div>
                    <Button onClick={() => this.props.onsubmit(this.state.picked)} bsStyle="primary">Submit</Button>
                </div>

              </div>


              )
    }
});
