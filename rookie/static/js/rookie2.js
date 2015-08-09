 $(function() {
    $("#datepicker1").datepicker();
  });
  $(function() {
    $("#datepicker2").datepicker();
  });

//wrapper for cloud search
function get_results(start){
    $("#results").html("");
    $("#search_status").html("");
    var term = $("#search_bar").val();
    $.post("/search?q=" + encodeURIComponent(term) + "&page=" + encodeURIComponent(String(start)), function(data){
            $("#results").html(data);
            $('.page').on("click", function(e){
               $("#pages").html("");
               var start_page = parseInt(this.id.replace("page_", ""));
               get_results(start_page);
            });
            $(".term").on("click", function(e){
                var term = $("#search_bar").val();
                var url = "http://localhost:5000/results?q=" + term + "&term=" +  this.id + "&page=" + $("#pages").attr("data-current-page") + "&termtype=" + this.getAttribute("data-term-type") + "&startdate=" + $("#datepicker1").val() + "&enddate=" + $("#datepicker2").val();
                location.href = url;
            });
        }
    );
}

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
