
$(document).ready( function() {

	// Affichage des details

	$('.less_detail').hide();
	$('.more_detail').hide();
	$('.txt_hide').hide();

	$('.more_detail').click(function(){
		$(this).hide('blind',{},500);
		$('#less_detail_'+$(this).attr('nb')).show('blind',{},500);
		$('#txt_hide_'+$(this).attr('nb')).show('blind',{},500);
	});

	$('.less_detail').click(function(){
		$(this).hide('blind',{},500);
		$('#more_detail_'+$(this).attr('nb')).show('blind',{},500);
		$('#txt_hide_'+$(this).attr('nb')).hide('blind',{},500);
	});

});

