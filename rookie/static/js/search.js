var url;

function search_records(){
  url  = 'https://s3-us-west-2.amazonaws.com/rookielens/results.html?term=';
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


$.get('https://s3-us-west-2.amazonaws.com/rookielens/data/keys.csv.gz', function(data){
  console.log("got data");
  values = data.split("\n");
  $( "#search_terms").autocomplete({
      source: values
    });
  }, 'text');