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
    this.setState({ showModal: false });
  },

  render() {


    return (
      <div >
        <Modal backdrop="static" show={this.state.showModal} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>Before you do the task, let's practice using the tool...</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>When you click close, you will see that there are <span style={{color: "#0028a3", fontWeight: "bold"}}>blue</span> spikes for articles that mention <span style={{color: "#0028a3", fontWeight: "bold"}}>United States</span>.</p>
            <p>Beneath the blue spikes, there are <span style={{color: "#b33125", fontWeight: "bold"}}>red</span> spikes for articles that also mention <span style={{color: "#b33125", fontWeight: "bold"}}>President Fidel Castro</span>.</p>

            <p>Try to use the slider to see what <span style={{color: "#0028a3", fontWeight: "bold"}}>United States</span> has to do with <span style={{color: "#b33125", fontWeight: "bold"}}>President Fidel Castro</span> during the time between <b>January 1994</b> to <b>January 1995.</b></p>

            <p>To do this, click the graph and slide your mouse to open the slider. You can click the black bars on each side to make it bigger or smaller.
               You can click the rectangle and slide to move the whole time range.
               Try to select January 1994 to January 1995.
               </p>

            <p>
            The reason to look at these dates is that the <span style={{color: "#0028a3", fontWeight: "bold"}}>blue</span> and <span style={{color: "#b33125", fontWeight: "bold"}}>red</span> spikes in that time range show that something might have happened involving the two men at that time.
            </p>

          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.close}>Close</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }

});
