$(document).ready(function(){
	var biomass = '';

	$('#biomassUploadButton').on('click', function(event){
		if ($(this).text() == "Upload")
		{
			$(this).text("Hide");

			$('#uploadBiomassDiv').show(300);
			$('#popover').popover({
			 	trigger: 'hover focus',
			 	container:'body', 
			 	placement:'top', 
			 	title:'Selecting Region', 
			 	content: 'Only select a region if you wish to apply allometric equations by species and not for the entire plot.'
				});
			$('#regionSelect').tooltip({
				 trigger: 'hover focus', 
				 placement: 'top', 
				 title: 'Setting this will apply equation by species.'
				})
			$('#regionSelect').trigger('change');
			$('#equationPopover').popover({
				trigger:'hover focus', 
				container:'body', 
				placement:'right', 
				title:'Equation Selector', 
				content: 'Select an equation that will run in the case of no equation listed for a species and/or region.'
			});

		}
		else
		{
			$(this).text("Upload");
			$('#uploadBiomassDiv').hide(300);

		}
	});

	$('#massPlotUploadButton').on('click', function(event){
		if ($(this).text() == "Upload") {
			$(this).text("Hide");

			$('#massPlotUpload').show(300);
		} else {
			$(this).text('Upload');
			$('#massPlotUpload').hide(300);
		}
	})

	$('#cancelUploadBiomass').on('click', function(event){
		biomass = '';
		$('#biomassUpload')[0].reset();
		$('#uploadBiomassDiv').hide(300);
	});

})