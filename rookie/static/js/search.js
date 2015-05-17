$("#search_button").on("click", function(){
    var query_string = '?' + $("#search_terms").val();
    console.log(query_string);
    window.location.href = '/rookie/search' + query_string;
});

