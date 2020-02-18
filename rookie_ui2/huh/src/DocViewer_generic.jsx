"use strict";
/*
Doc viewer: generic
*/

var React = require('react');

import DocViewer_baseline from './DocViewer_baseline.jsx';
import DocViewer from "./DocViewer.jsx";


export default class DocViewer_generic extends React.Component{

    getDocViewer(){
        if (this.props.kind_of_doc_list == "summary_baseline"){
            return <DocViewer_baseline {...this.props}/>
        }else{
            return <DocViewer {...this.props}/>
        }
    }
    render(){
      return this.getDocViewer();
    }
}
