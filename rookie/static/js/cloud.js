var numbers = window.data.slice(0, 1 + 9);

var width = $("#vis").width();

var max_x = _.max(numbers, function(number){ return number.score; });

max_x = max_x.score;

var x = d3.scale.linear()
    .domain([0, max_x])
    .range([0, 100]);

d3.select("#vis")
  .selectAll("div")
    .data(numbers)
  .enter().append("div")
    .style("height", function(d) { 
      return x(d.score) + "px";
    })
    .style("color", "green")
    .style("background-color", "grey")
    .text(function(d) { return d.fulltext; });