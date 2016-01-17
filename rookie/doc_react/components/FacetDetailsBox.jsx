"use strict";
/*
Facet Details box
*/

var React = require('react');
var FacetPreviewList = require('./FacetPreviewList.jsx');

module.exports = React.createClass({

    render: function(){
        let row = {
          width:"100%",
          overflow:"hidden",
          height:this.props.rw_height
        };
        let binsize = this.props.bin_size;
        return(
           <div>
                {this.props.bins.map((x, i) =>
                    <div key={i} style={row}>
                        <FacetPreviewList active={this.props.f} items={x.facets} onClick={this.props.handleF}/>
                    </div>
                )}
           </div>
        );
       }
});