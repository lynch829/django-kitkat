$(document).ready(function(){

console.log("home.js")

//change options for machine once test type has been selected since some tests do not apply to some machines
$("#id_qa_test_def_id").change(function(){
	//console.log("in the change function")
	var test_name = $(this).find(":selected").text();
	$.get('/kitkat/list_machines_for_test/', {test_name: test_name}, function(data){
		//$("#ajax_test").append(data)
		//we expect values a string of machine names returned as a string delimited by "##"
		//followed by a string of their primary keys.  The two strings are separated by "/"
		var lists = data.split("/")
		var new_machine_options = lists[0].split("##")
		var primary_keys = lists[1].split("##")
		var $machine_select = $("#id_machine_id");
		var machine_already_selected = $machine_select.find(":selected").val()
		$machine_select.empty();
		$machine_select.append($("<option></option>").attr("value","").text("---------"));
		for(var i=0; i<new_machine_options.length; i++){
			if(primary_keys[i] == machine_already_selected){
				$machine_select.append($("<option selected='selected'></option>").attr("value",primary_keys[i]).text(new_machine_options[i]));
				}
			else{
				$machine_select.append($("<option></option>").attr("value",primary_keys[i]).text(new_machine_options[i]));
				}
			}
/*
var $el = $("#selectId");
$el.empty(); // remove old options
$.each(newOptions, function(value,key) {
  $el.append($("<option></option>")
     .attr("value", value).text(key));
});
*/
		
})

})

});
