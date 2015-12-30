"use strict";
var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');

var Doc = React.createClass({
    handleClick: function(e) {
        this.props.onMouseOver(e);
        this.forceUpdate();
    },
    render: function() {
         let tmp = this.props.color;
         var divStyle = {
            color: tmp
         }
         var lstyle = {
            float: "left"
         }
         return (
          <div>
            <div style={lstyle}>{this.props.pubdate}</div>
            <div style={divStyle} name={this.props.name} onMouseOver={this.handleClick.bind(this, this.props.name)}>
              {this.props.headline}
            </div>
          </div>);
    }
});

var DocList = React.createClass({
  getInitialState(){
    return {active: -1};
  },
  handleClick: function(item) {
    this.setState({active: item});
  },
  render: function() {
    var sorted = _.sortBy(this.props.items, function(n) {
      return n.rank;
    });
    var snippets = false;
    if (snippets === true){
      var story_budget = this.props.height / (this.props.fontpx * 3);
    }else{
      var story_budget = this.props.height / (this.props.fontpx);
    }
    var divStyle = {
      border: '1px solid green'
    }
    return (
      <div style={divStyle}>
        {this.props.items.map(function(bin, i) {
          return (<div>
          {bin.docs.map(function(item, i) {
            let csolor;
            if (item.rank < story_budget){
              if (this.state.active===this.props.items[i].key){
                  csolor="blue";
              }else{
                  csolor="red";
              }
              return (
                <Doc name={item.key} pubdate={item.pubdate} headline={item.headline} color={csolor} onMouseOver={this.handleClick} key={i}/>
              );
            }
          }, this)}
          </div>)
        }, this)}
      </div>
    );
  }
});

var datas = [
  {"bin":"2010", "docs":[ 
      {"key": "mitch", "rank":"9", "pubdate": "1/10/2010", "headline": "the police are bad"},
      {"key": "dave", "rank":"2", "pubdate": "3/4/2010", "headline": "the mayor is great"}]},
  {"bin":"2011", "docs":[ 
      {"key": "bll", "rank":"8", "pubdate": "5/14/2011", "headline": "the dog park is a mess"},
      {"key": "sam", "rank":"4", "pubdate": "1/9/2011", "headline": "the levees are broken"},
      {"key": "as", "rank":"5", "pubdate": "2/2/2011", "headline": "the firefighters need money"}]},
  {"bin":"2012", "docs":[
      {"key": "bob", "rank":"6", "pubdate": "2/14/2012", "headline": "the city hall is broken"},
      {"key": "joe", "rank":"1", "pubdate": "2/15/2012", "headline": "the teachers are mad"}]}
  ];

ReactDOM.render(
  <DocList items={datas} fontpx={12} height={50}/>,
  document.getElementById('example')
);