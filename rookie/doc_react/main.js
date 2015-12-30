"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');

var BinDocs = React.createClass({
    render: function() {
        var snippets = false;
        if (snippets === true){
          var story_budget = (this.props.bin_height / (this.props.fontpx * 3)) - 1;
        }else{
          var story_budget = (this.props.bin_height / (this.props.fontpx)) - 1;
        }
        console.log(story_budget);
        var divStyle = {
          border: '1px solid yellow'
        }
        return (
          <div style={divStyle}>
              {this.props.docs.map(function(item, i) {
                if (item.rank < story_budget){
                    return <div key={i}>{item.headline}</div>
                  }
                }, this)
              }
          </div>);
    }
});

var DocBins = React.createClass({
  render: function() {
    var divStyle = {
      border: '1px solid green'
    }
    var docsStyle = {
      float: 'right'
    }
    var datesStyle = {
      float: 'left'
    }
    var bin_height = this.props.height / this.props.items.length;
    var binStyle = {
      height: bin_height,
      border: '1px solid pink'
    }
    return (
      <div style={divStyle}>
        {this.props.items.map(function(item, i) {
            return <div key={i} style={binStyle}><div style={datesStyle}>{item.bin}</div><div style={docsStyle}><BinDocs bin_height={bin_height} fontpx={this.props.fontpx} docs={item.docs}/></div></div>
          }, this)
        }
      </div>
    );
  }
});


var datas = [
  {"bin":"2010", "docs":[ 
      {"key": "mitch", "rank":"1", "pubdate": "1/10/2010", "headline": "the police are bad"},
      {"key": "dave", "rank":"2", "pubdate": "3/4/2010", "headline": "the mayor is great"}]},
  {"bin":"2011", "docs":[ 
      {"key": "bll", "rank":"3", "pubdate": "5/14/2011", "headline": "the dog park is a mess"},
      {"key": "sam", "rank":"2", "pubdate": "1/9/2011", "headline": "the levees are broken"},
      {"key": "as", "rank":"1", "pubdate": "2/2/2011", "headline": "the firefighters need money"}]},
  {"bin":"2012", "docs":[
      {"key": "bob", "rank":"2", "pubdate": "2/14/2012", "headline": "the city hall is broken"},
      {"key": "joe", "rank":"1", "pubdate": "2/15/2012", "headline": "the teachers are mad"}]}
  ];

ReactDOM.render(
  <DocBins items={datas} fontpx={12} height={110}/>,
  document.getElementById('example')
);