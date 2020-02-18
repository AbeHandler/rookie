"use strict";
/*
A Q or and F and a click handler
*/

var React = require('react');

export default class ClickableQF extends React.Component{

     render(){
        let x_script;
        let x_handler = this.props.xHandler;
        if (this.props.showX){
            x_script = <sup onClick={x_handler} style={{color: "black", cursor: "pointer"}}>X</sup>
        }else{
            x_script = ""
        }
        return (
            <span onClick={()=>this.props.click(this.props.text)} style={{color: this.props.color, fontWeight: "bold"}}>
                {this.props.text}{x_script}
            </span>
        );
    }
}
