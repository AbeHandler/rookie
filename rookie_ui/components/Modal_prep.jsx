"use strict";
/*
A result in a normal IR system
*/

var React = require('react');

var Modal = require('react-bootstrap/lib/Modal');
var Button = require('react-bootstrap/lib/Button');

module.exports = React.createClass({

getInitialState() {

    return { showModal: true };
  },

  close() {
    this.props.unmodal();
  },

  render() {

    return (
      <div>
        <Modal backdrop="static" dialogClassName="custom-modal" show={this.state.showModal} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>Get ready...</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            You are going to use a search tool to figure out which of these statements is true:

            <ul>
              {this.props.answers.map(function(k, v){
                return (<li>{k}</li>)
              })}
            </ul>

            You will be asked to copy and paste two sentences from the bottom right that give evidence for your answer.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.close}>OK. Ready!</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }

});
