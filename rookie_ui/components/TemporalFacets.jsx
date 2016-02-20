/* jshint node: true */

/**
TFacts: a list of temporal facets (ex. [2010, 2011 ... 2015])
*/

"use strict";
var React = require('react');
var _ = require('lodash');
var moment = require('moment');

var YearBin = require('./YearBin.jsx');
var MonthBinList = require('./MonthBinList.jsx');

module.exports = React.createClass({
    
    /**
     * Take docs and bin key size. return bin keys
     * @returns {[binkey, binkey... binkey]} ex([2010, 2011 ... 2015])
     */
    get_bin_keys: function(){
        if (this.props.bin_size == "year"){
            let years = _.map(this.props.docs, function(n){
                return parseInt(n.year);
            });
            years = _.uniq(years);
            years = _.sortBy(years, function(n){
                return n;
            });
            return years;
        }
        return "TODO";
    },

    /**
     * Counts occurace of a facet in a timespan
     * @param {f} facet - string. Key of vars.
     * @param {moment} start - start of span
     * @param {moment} end - end of span
     * @returns {int} sum
     */
    count_in_range: function(f, start, end){
        let sum = 0;
        let q_data = this.props.q_data;
        let vars = this.props.f_counts; // todo this is given
        return 0;
        return sum;
    },

    /**
     * Take a bin key (string) and return a pair of moment objects
     * @param {string} key - ex: "2011" or "Mar 2011"
     * @returns {[moment, moment]} start and end of range
     */
    bin_key_to_range: function(key){
        let output = {};
        if (/^(19|20)\d{2}$/.test(key)){
            output.start = moment(key + "-01-01");
            output.end = moment(key + "-12-31");
            return output;
        }
        //untested... -->
        if (/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (19|20)\d{2}$/.test(key)){
            //output["start"] = moment(key + "-01-01");
            //output["end"] = moment(key + "-12-31");
            return output;
        }
    },

    get_n_docs_in_bin: function(bin_key){
        let start_end = this.bin_key_to_range(bin_key);
        return this.count_in_range(this.props.f, start_end.start, start_end.end);
    },

    isSelected: function(key, binsize) {
        if (binsize == "year" & (this.props.yr_start.toString() == this.props.yr_end.toString())){
            if (this.props.yr_start.toString() == key){
                return true;
            }
        }
        return false;
    },

    handleMo: function(e){
        this.props.handleMo(e);
    },

    get_selected_mo: function(){
        if (this.props.mo_start == this.props.mo_end & this.props.mo_start != -1 & this.props.mo_end != -1){
            return this.props.mo_start;
        }
        return -1;
    },

    render: function(){
        let binkeys = this.get_bin_keys();
        let ndocs = this.get_n_docs_in_bin;
        let bins = _.map(binkeys, function(n){
                    return [n, ndocs(n)];
                    });
        let binclick = this.props.handleBinClick;
        let bin_size = this.props.bin_size;
        let sel = this.isSelected;
        let rw_height = this.props.rw_height;
        let mo_bins;
        let selected_fn = this.get_selected_mo;
        if(this.props.n_results == 0){
            return <div></div>
        }
        if (this.props.show_months){
           let right = {
            "width":"50%",
            "float":"left"
           };  
           return <div>
                    <div style={right}>
                        <div>
                        {_.map(bins, function(n){
                            return <div key={n[0]}><YearBin rw_height={rw_height} selected={sel(n[0], bin_size)} handleBinClick={binclick} text={n[0]} n_results={n[1]}/></div>;
                        })}
                        </div>
                    </div>
                    <div style={right}><MonthBinList selected_mo={this.get_selected_mo()} handleMo={this.handleMo} height={this.props.height}/></div>
                  </div>
        }else{
            return (<div>
                {_.map(bins, function(n){
                    return <div key={n[0]}><YearBin rw_height={rw_height} selected={sel(n[0], bin_size)} handleBinClick={binclick} text={n[0]} n_results={n[1]}/></div>;
                })}
                </div>); 
        }
    }
});