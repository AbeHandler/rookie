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
    console.log(sorted);
    return (
      <div>
        {this.props.items.map(function(item, i) {
          let csolor;
          if (this.state.active===this.props.items[i].key){
              csolor="blue";
          }else{
              csolor="red";
          }
          return (
            <Doc name={item.key} pubdate={item.pubdate} headline={item.headline} color={csolor} onMouseOver={this.handleClick} key={i}/>
          );
        }, this)}
      </div>
    );
  }
});

var datas = [
  {"key": "mitch", "rank":"9", "pubdate": "1/10/2015", "headline": "the police are bad"},
  {"key": "dave", "rank":"2", "pubdate": "3/4/2012", "headline": "the mayor is great"},
  {"key": "bll", "rank":"8", "pubdate": "5/14/2010", "headline": "the dog park is a mess"},
  {"key": "sam", "rank":"4", "pubdate": "1/9/2010", "headline": "the levees are broken"},
  {"key": "as", "rank":"5", "pubdate": "2/2/2013", "headline": "the firefighters need money"},
  {"key": "3", "rank":"6", "pubdate": "2/14/2013", "headline": "the city hall is broken"},
  {"key": "4", "rank":"1", "pubdate": "2/15/2013", "headline": "the teachers are mad"},
  {"key": "5", "rank":"3", "pubdate": "1/9/2014", "headline": "the state lost money"},
  {"key": "43", "rank":"7", "pubdate": "1/2/2014", "headline": "bla bla the restaurants in the marigny"},
]


ReactDOM.render(
  <DocList items={datas} height={50}/>,
  document.getElementById('example')
);