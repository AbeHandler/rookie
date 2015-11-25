var width = $("#results").width();
var height = 500;

var words = window.data.slice(1,10);
var position = 1;

words.forEach(function(entry) {
    entry['position'] = position;
    position = position + 1;
})

var word = "gongoozler";

var holder = d3.select("#results")
      .append("svg")
      .attr("width", width)    
      .attr("height", height); 

// draw a rectangle
holder.selectAll("g")
    .data(words)
    .enter()
    .append("a")
    .attr("xlink:href", function(d){
      return d.url;
    });

holder.selectAll("a").
    append("text").
    text(function(d){return d.fulltext}).
    attr("x", 0).
    attr("y",  function(d){
      return (d.position * 50); 
    });