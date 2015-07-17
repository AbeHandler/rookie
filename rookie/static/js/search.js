var url;

$("#search_terms_combo").combobox();

function search_records(){
  url  = 'https://s3-us-west-2.amazonaws.com/rookielens/results.html?term=';
  if ($("#search_terms").val() != ""){
    url = url + $("#search_terms_combo").val();
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

try{
  var s = new RegExp('(=)(.{1,})');
  q = '<option value="' + decodeURIComponent(s.exec(location.search)[2]) + '">' + decodeURIComponent(s.exec(location.search)[2]) + '</option>'
  $("#search_terms_combo").append(q);
  $("#search_terms_combo").combobox();
}
catch(err){
  console.log("can't find a term from the URL")
}

$.get("https://s3-us-west-2.amazonaws.com/rookielens/data/searchbar.html.gz", function(d){
  $("#search_terms_combo").append(d);
});