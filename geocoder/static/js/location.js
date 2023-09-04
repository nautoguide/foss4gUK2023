window.locateClick = function(cords) {
	document.getElementById("search-input").value = "";
	Unicorn.trigger("location_search","searchkey");
	document.getElementById("submit-search").click();

	window.map.clearSelected();
	$.ajax({
		url: `/location/reversegeocoder/${cords[0]}/${cords[1]}`,
		data: {
			'page_size': 10,
		},
		success: function (data) {
			let postcode=data.results[0].properties.postcode;
			if(postcode==='')
				postcode=data.results[0].properties.postcode_district
			$('#search-input').val(`${postcode}`);

		}
	});
}