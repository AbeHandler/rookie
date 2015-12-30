"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');

var Bin = React.createClass({
    render: function() {
        var divStyle = {
          border: '1px solid yellow',
          width: '100%'
        }
        var lStyle = {
          float: 'left',
          width: '80px'
        }
        var headlineStyle = {
          float: 'left'
        }
        let articleheight = this.props.fontpx + 15;
        var articleStyle = {
          height: articleheight
        }
        var snippets = false;
        if (snippets === true){
          var story_budget = (this.props.bin_height / (this.props.fontpx * 3)) - 1;
        }else{
          var story_budget = this.props.bin_height / articleheight;
          console.log("no snippets");
        }
        return (
          <div style={divStyle}>
              {this.props.docs.map(function(item, i) {
                if (item.rank < story_budget){
                    return <div key={i} style={articleStyle}><div style={lStyle}>{item.pubdate}</div><div style={headlineStyle}>{item.headline}</div></div>
                  }
                }, this)
              }
          </div>);
    }
});

var DocBins = React.createClass({
  handleClick: function(e) {
    this.props.onClick(e);
  },
  render: function() {
    var divStyle = {
      border: '1px solid green'
    }
    var docsStyle = {
      float: 'right',
      width: '95%'
    }
    var datesStyle = {
      float: 'left',
      width: '5%'
    }
    var bin_height = this.props.height / this.props.items.length;
    var binStyle = {
      height: bin_height,
      border: '1px solid pink'
    }
    return (
      <div style={divStyle}>
        {this.props.items.map(function(item, i) {
            return <div key={i} style={binStyle}><div style={datesStyle} onClick={this.handleClick.bind(this, item.bin)}>{item.bin}</div><div style={docsStyle}><Bin bin_height={bin_height} fontpx={this.props.fontpx} docs={item.docs}/></div></div>
          }, this)
        }
      </div>
    );
  }
});

var BigBin = React.createClass({
  render: function() {
    var divStyle = {
      border: '1px solid green'
    }
    var docsStyle = {
      float: 'right',
      width: '95%'
    }
    var datesStyle = {
      float: 'left',
      width: '5%'
    }
    var bin_height = this.props.height;
    var binStyle = {
      height: bin_height,
      border: '1px solid pink'
    }
    return (
      <div style={divStyle}>
        {this.props.items.map(function(item, i) {
            if (item.bin == this.props.bin){
              return <div key={i} style={binStyle}><div style={datesStyle} onClick={this.handleClick}>{item.bin}</div><div style={docsStyle}><Bin bin_height={bin_height} fontpx={this.props.fontpx} docs={item.docs}/></div></div>
            }
          }, this)
        }
      </div>
    );
  }
});

var Viewer = React.createClass({
  getInitialState(){
    return {mode: "zoomOut", bin: "None"};
  },
  handleClick: function(item) {
    this.setState({bin: item});
    this.setState({mode: "zoomIn"});
  },
  xZoom: function(item) {
    this.setState({bin: "None"});
    this.setState({mode: "zoomOut"});
  },
  render: function() {
    if (this.state.mode==="zoomIn"){
      return (<div><div>u r zoomedIn <span onClick={this.xZoom}>X</span></div><BigBin items={datas} bin={this.state.bin} fontpx={12} height={200}/></div>)
    }else{
      return (<div><div>u r zoomedOut</div><DocBins items={datas} onClick={this.handleClick} fontpx={12} height={200}/></div>)
    }
  }
});


var datas = [
  {"bin":"2010", "docs":[ 
      {"key": "mitch", "rank":"1", "pubdate": "1/10/2010", "headline": "City cancels plans for Super Bowl drone despite enthusiasm and interest from NOPD"},
      {"key": "dave", "rank":"2", "pubdate": "3/4/2010", "headline": "Emergency meeting on jail reform raises questions about notification"}]},
  {"bin":"2011", "docs":[ 
      {"key": "bll", "rank":"3", "pubdate": "1/14/2011", "headline": "City agency cant reach consensus, so corner-store demolition is denied"},
      {"key": "sam", "rank":"2", "pubdate": "2/9/2011", "headline": "Crescent City board faces building issues"},
      {"key": "sam", "rank":"5", "pubdate": "3/12/2011", "headline": "Mayor to meet with firefighers union"},
      {"key": "sam", "rank":"4", "pubdate": "5/15/2011", "headline": "911 dispatch center gets upgrade"},
      {"key": "sam", "rank":"6", "pubdate": "8/20/2011", "headline": "NOPD, Justice Department to meet"},
      {"key": "sam", "rank":"7", "pubdate": "9/9/2011", "headline": "Pride College prep will close in December"},
      {"key": "as", "rank":"1", "pubdate": "11/2/2011", "headline": " City looking to spend federal money more efficiently, quickly"}]},
  {"bin":"2012", "docs":[
      {"key": "bob", "rank":"2", "pubdate": "2/14/2012", "headline": "Landrieu drops plans to create civic center at former Charity Hospital"},
      {"key": "joe", "rank":"1", "pubdate": "2/15/2012", "headline": "Board says RSD will recommend against charter renewal"}]}
  ];

ReactDOM.render(
  <Viewer/>,
  document.getElementById('example')
);