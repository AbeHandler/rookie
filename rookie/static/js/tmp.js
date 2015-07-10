$(".result").on("click", function(e){
	var clickedid = $(this).attr('id');
	$("#" + clickedid).toggle( "fast" );
});