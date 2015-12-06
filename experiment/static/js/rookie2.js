
$(".facet").on("click", function() {
  var term = this.id.replace("-label", "");
  var termtype = $("[id='" + this.id + "']").attr("data-termtype");
  $.post("get_snippet_post?term=" + term + "&termtype=" + termtype, function (data) {
    $("[id='detail-panel']").html(data);
    $(".extract").on("click", function () {
      var docid = this.attributes['data-doc'].value;
      var dataterm = this.attributes['data-term'].value;
      var q = $("#search_bar").val();
      var url = "/detail?q=" + q + "&docid=" + docid + "&t=" + dataterm;
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

function get_results(start){
    $("#results").html("");
    $("#search_status").html("");
    var term = $("#search_bar").val();
    var url = "/facets?q=" + term + "&page=" + start;
    window.location.href = url;
}

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

  function reload_big_viz(){
    var term = $("#search_bar").val();
    var url = "/bigviz?q=" + term;
    window.location.href = url;
  }

  $('#search_button_big_viz').on('click', function(){
    reload_big_viz();
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


 $('body').bind('keypress', function(e){
   if (window.location.pathname.includes("bigviz")){
      if ( e.keyCode == 13 ) {
       reload_big_viz();
     }
   }else{
      if ( e.keyCode == 13 ) {
       get_results(1);
      }
   }
 });

 $(".facet").on("click", function(){
   $(".term").removeClass("selected");
   $("[id='" + this.id + "']").addClass("selected");
 });

  $("#search_bar").val($.QueryString["q"]);