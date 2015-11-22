
$(".facet").on("click", function() {
  var term = this.id.replace("-label", "");
  var termtype = $("[id='" + this.id + "']").attr("data-termtype");
  $.post("get_snippet_post?term=" + term + "&termtype=" + termtype, function (data) {
    $("[id='detail-panel']").html(data);
    $(".extract").on("click", function () {
      var docid = this.attributes['data-doc'].value;
      var dataterm = this.attributes['data-term'].value;
      var q = $("#search_bar").val();
      var url = "http://" + "{{IP}}" + "/detail?q=" + q + "&docid=" + docid + "&t=" + dataterm;
      window.location.href = url;
    });
    bold_q();
  })
});

 jQuery.fn.exists = function(){return this.length>0;}

 if ($("#datepicker1").exists() && $("#datepicker2").exists()){
  $(function() {
    $("#datepicker1").datepicker();
  });
  $(function() {
    $("#datepicker2").datepicker();
  });
}

//wrapper for cloud search
function get_results(start){
    $("#results").html("");
    $("#search_status").html("");
    var term = $("#search_bar").val();
    var url = "http://" + "{{IP}}" + "/facets?q=" + term;
    window.location.href = url;
}

$('.page').on("click", function(e){
  $("#pages").html("");
  var start_page = parseInt(this.id.replace("page_", ""));
  get_results(start_page);
});

function bold_q(){
  var qtoks = $("#search_bar").val().split(" ");
  for (i = 0; i < qtoks.length; i++) { 
    $("[data-word='" + qtoks[i] + "']").css("font-weight", "bold");
  }
  var elementExists = document.getElementById("search_button");
  if ($('.selected').length > 0){
     var ftoks = $(".selected").first().html().split(" ");
     for (i = 0; i < ftoks.length; i++) { 
       $("[data-word='" + ftoks[i] + "']").addClass("selected");
     }  
  }
}


 $('#search_button').on('click', function(){
    get_results(1);
 });
  
 //https://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript 
 (function($) {
    $.QueryString = (function(a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'))
 })(jQuery);

 $("#search_bar").val($.QueryString["q"]);
 $("#advanced_search").on("click", function(){$(".toggler").toggle()});

 $('body').bind('keypress', function(e){
   if ( e.keyCode == 13 ) {
     get_results(1);
   }
 });

 $(".facet").on("click", function(){
   $(".term").removeClass("selected");
   $("[id='" + this.id + "']").addClass("selected");
 });