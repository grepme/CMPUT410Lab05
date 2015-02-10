
$("button[data-action='delete']").click(function(){
	$.post("/delete", {'rowid': $(this).attr('data-id')}, function(data){
		if (data.status)
			window.location.reload();
		else
			alert('Failed to delete task!');
	});
});
$("a[data-login='true']").click(function(){
	$('#login_form').slideToggle();
});
$("a[data-login='false']").click(function(){
	$.get('/logout', function(){
		window.location.reload();
	});
});
if ($("p[data-notify='true']")){
	window.setTimeout(function(that){
		$("p[data-notify='true']").each(function(){
			$(this).slideUp();
		});
	}, 5000);
}
