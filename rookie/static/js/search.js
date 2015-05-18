function search_records(){
    var query_string = '?q=' + $("#search_terms").val();
    console.log(query_string);
    $.post('/rookie/search' + query_string, function(results){
        $("#results").html(results);
        $("#timeline").html("Insert semantic timeline here");
    });
}


$("#search_button").on("click", function(){
   search_records();
});

$("body").keypress(function(e) {
  if(e.which == 13) {
    search_records();
  }
});