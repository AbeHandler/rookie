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
    var url = "http://54.187.8.229/testing?q=" + term;
    window.location.href = url;
}

$('.page').on("click", function(e){
  $("#pages").html("");
  var start_page = parseInt(this.id.replace("page_", ""));
  get_results(start_page);
});

$(".term").on("click", function(e){
  var term = $("#search_bar").val();
  var url = "http://52.27.242.183/results?q=" + term + "&term=" +  this.id + "&page=" + $("#pages").attr("data-current-page") + "&termtype=" + this.getAttribute("data-term-type") + "&startdate=" + $("#datepicker1").val() + "&enddate=" + $("#datepicker2").val();
   location.href = url;
});

//stackoverflow.com/questions/923299/how-can-i-detect-when-the-mouse-leaves-the-window
function addEvent(obj, evt, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evt, fn, false);
    }
    else if (obj.attachEvent) {
        obj.attachEvent("on" + evt, fn);
    }
}

addEvent(document, "mouseout", function(e) {
    e = e ? e : window.event;
    var from = e.relatedTarget || e.toElement;
    if (!from || from.nodeName == "HTML") {
       // $('#myModal').foundation('reveal', 'open');
    }
});

/*
 $('body').bind('keypress', function(e){
   if ( e.keyCode == 13 ) {
     post_answer()
   }
 });

 $('#enter').on('click', function(e){
     post_answer()
 });
*/


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

 function post_answer(){
   var name = $("#name").val()
  $.post( "/answer/" + name, function( data ) {
   alert(data);
  });
 }
