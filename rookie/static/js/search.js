var url;

function search_records(){
	url  = 'http://localhost:5000/rookie/search?q=';
	if ($("#search_terms").val() != ""){
    url = url + $("#search_terms").val();
  }
  console.log(url);
  window.location = url;
}

$("#search_button").on("click", function(){
   search_records();
});

$("body").keypress(function(e) {
  if(e.which == 13) {
    search_records();
  }
});

 $( document ).ready(function() {
  for(var i=0; i<window.people.length; i++) {
    $("#people").append(window.people[i].name + "<br>");
  }
  for(var i=0; i<window.organizations.length; i++) {
    $("#organizations").append(window.organizations[i].name + "<br>");
  }
  for(var i=0; i<window.results.length; i++) {
    $("#results").append('<a href="'+ window.results[i].url + '">' + window.results[i].headline + '</a><br>');
  }
});