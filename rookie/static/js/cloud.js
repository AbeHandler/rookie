
      //Width and height
      var w = 300;
      var h = 500;

      //Original data
      var dataset = [
        [
          { x: 0, y: 5 }
        ],
        [
          { x: 0, y: 10 }
        ],
        [
          { x: 0, y: 22 }
        ]
      ];

      //Set up stack method
      var stack = d3.layout.stack();

      //Data, stacked
      stack(dataset);

      //Set up scales
      var xScale = d3.scale.ordinal()
        .domain(d3.range(dataset[0].length))
        .rangeRoundBands([0, w], 0.05);
    
      var yScale = d3.scale.linear()
        .domain([0,       
          d3.max(dataset, function(d) {
            return d3.max(d, function(d) {
              return d.y0 + d.y;
            });
          })
        ])
        .range([0, h]);
        
      //Easy colors accessible via a 10-step ordinal scale
      var colors = d3.scale.category10();
    
      //Create SVG element
      var svg = d3.select("#vis")
            .append("svg")
            .attr("width", w)
            .attr("height", h);
  
      // Add a group for each row of data
      var groups = svg.selectAll("g")
        .data(dataset)
        .enter()
        .append("g")
        .style("fill", function(d, i) {
          return colors(i);
        });
  
      // Add a rect for each data value
      var rects = groups.selectAll("rect")
        .data(function(d) { return d; })
        .enter()
        .append("rect")
        .attr("x", function(d, i) {
          return xScale(i);
        })
        .attr("y", function(d) {
          return yScale(d.y0);
        })
        .attr("height", function(d) {
          return yScale(d.y);
        })
        .attr("width", xScale.rangeBand());