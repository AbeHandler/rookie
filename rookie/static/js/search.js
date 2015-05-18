$("#search_button").on("click", function(){
    var query_string = '?q=' + $("#search_terms").val();
    console.log(query_string);
    $.post('/rookie/search' + query_string, function(results){
    	$("#results").html(results);
    });
});

