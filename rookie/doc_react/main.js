"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');

var BinDocs = React.createClass({
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
            return <div key={i} style={binStyle}><div style={datesStyle}>{item.bin}</div><div style={docsStyle}><BinDocs bin_height={bin_height} fontpx={this.props.fontpx} docs={item.docs}/></div></div>
          }, this)
        }
      </div>
    );
  }
});


var datas = [
  {"bin":"2010", "docs":[ 
      {"key": "mitch", "rank":"1", "pubdate": "1/10/2010", "headline": "City cancels plans for Super Bowl drone despite enthusiasm and interest from NOPD"},
      {"key": "dave", "rank":"2", "pubdate": "3/4/2010", "headline": "Emergency meeting on jail reform raises questions about notification"}]},
  {"bin":"2011", "docs":[ 
      {"key": "bll", "rank":"3", "pubdate": "5/14/2011", "headline": "City agency cant reach consensus, so corner-store demolition is denied"},
      {"key": "sam", "rank":"2", "pubdate": "1/9/2011", "headline": "Crescent City board faces building issues"},
      {"key": "as", "rank":"1", "pubdate": "2/2/2011", "headline": " City looking to spend federal money more efficiently, quickly"}]},
  {"bin":"2012", "docs":[
      {"key": "bob", "rank":"2", "pubdate": "2/14/2012", "headline": "Landrieu drops plans to create civic center at former Charity Hospital"},
      {"key": "joe", "rank":"1", "pubdate": "2/15/2012", "headline": "Board says RSD will recommend against charter renewal"}]}
  ];

ReactDOM.render(
  <DocBins items={datas} fontpx={12} height={200}/>,
  document.getElementById('example')
);