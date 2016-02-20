"use strict";
/*

*/

var React = require('react');
var FacetPreviewList = require('./FacetPreviewList.jsx');

module.exports = React.createClass({
    handleHoverIn: function(item) {
      this.props.handleHoverIn(item);
    },
    handleHoverOut: function(item) {
      this.props.handleHoverOut(item);
    },
    render: function(){
        let row = {
          width:"100%",
          overflow:"hidden",
          height:this.props.rw_height
        };
        let binsize = this.props.bin_size;
        let hoverIn = this.props.handleHoverIn;
        let hoverOut = this.props.handleHoverOut;
        let handleBinClick = this.props.handleBinClick;
        return(
           <div>
                {this.props.bins.map((x, i) =>
                    <div key={i} style={row}>
                        <FacetPreviewList handleHoverIn={hoverIn} handleHoverOut={hoverOut} hovered={this.props.hovered} active={this.props.f} items={x.facets} handleBinClick={handleBinClick}/>
                    </div>
                )}
           </div>
        );
       }
});