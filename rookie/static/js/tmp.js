$(".result").on("click", function(e){
	var clickedid = $(this).attr('id') + "-details";
	$("#" + clickedid).toggle( "fast" );
});