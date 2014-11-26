function initialize() {

var input = document.getElementById('searchTextField');
var autocomplete = new google.maps.places.Autocomplete(input,{
	types:['establishment']});


var input2 = document.getElementById('searchTextField2');
var autocomplete2 = new google.maps.places.Autocomplete(input2);


var input3 = document.getElementById('searchTextField3');
var autocomplete3 = new google.maps.places.Autocomplete(input3);
}

google.maps.event.addDomListener(window, 'load', initialize);


