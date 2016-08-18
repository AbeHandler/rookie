'use strict';
/*
Question.jsx
*/

var React = require('react');
var ReactDOM = require('react-dom');
module.exports = React.createClass({

  getInitialState: function(){
    return {"picked": -1}
  },

  change: function(e){
      this.setState({picked: e});
  },

  render: function() {
    
    let width = this.props.width;
    let height = this.props.height;

    let tmp = this.change;
    let ans = this.props.answers;
      return (
              <form>
                    {this.props.answers.map(function(k, v){
                      return (<div><input type="radio" name="1" value="1" onClick={() => tmp(v)}/> {k} </div>)
                    })}
                </form>
              )
    }
});
