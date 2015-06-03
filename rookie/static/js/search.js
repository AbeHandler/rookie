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
    var headlines = _.uniq(window.data, function(item) { return item.headline; });
    $(headlines).each(function(e) {
      var compiled = _.template("<a href='<%= url %>'><%= headline %></a></br>"); 
      var temp = compiled({url: this.url, headline: this.headline});
      $("#results").append(temp);
    });
});