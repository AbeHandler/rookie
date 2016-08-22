"use strict";
/*
A result in a normal IR system
*/

var React = require('react');

var Modal = require('react-bootstrap/lib/Modal');
var Button = require('react-bootstrap/lib/Button');

module.exports = React.createClass({

  getInitialState() {
      return { showModal: false };
    },

    close() {
      this.props.close();
    },

  render() {

    return (
      <div >
        <Modal backdrop="static" show={this.props.show} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>You got it!</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Good job! See how the box in the bottom right of the screen now shows what the <span style={{color: "#0028a3", fontWeight: "bold"}}>United States</span> has to do with <span style={{color: "#b33125", fontWeight: "bold"}}>President Fidel Castro</span> from <b>January 1994</b> to <b>January 1995?</b>
             <p/>
             <p>Use that information to answer the question in the bottom left.</p>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.close}>OK</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }

});
