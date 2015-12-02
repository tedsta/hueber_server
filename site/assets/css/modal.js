var frameSrc = "/login";

$('#openBtn').click(function(){
    $('#myModal').on('show', function () {

        $('iframe').attr("src",frameSrc);
      
	});
    $('#myModal').modal({show:true})
});