"use strict";
/*
A result in a normal IR system
*/

var React = require('react');

var Modal = require('react-bootstrap/lib/Modal');
var Button = require('react-bootstrap/lib/Button');
var moment = require('moment');

module.exports = React.createClass({

  getInitialState() {
      return { showModal: false };
    },

    close() {
      this.props.close();
    },

  render() {

    var props = this.props;
    return (
      <div >
        <Modal backdrop="static" show={this.props.show} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>{this.props.headline}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {props.sents.map(function(sent, n) {
                if (n == 0){
                  return (
                    <p>
                      <span style={{color: "grey"}}>{moment(props.pubdate).format("MMM. DD YYYY")} &mdash; </span>
                      {sent}
                    </p>
                  )
                }else{
                return  <p>
                          {sent}
                        </p>
                }
            })}
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.close}>Done</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }

});
