$(document).ready(function(){
console.log("document ready")
var request_number = 1

$("#additional_filters_button").click(function(){
	console.log("...")
		var test_name = $("#id_qa_test_def_id").find(":selected").text()
		var test_val = $("#id_qa_test_def_id").find(":selected").val()
		var attribute_pk = $("#select_attribute").find(":selected").val()
		if(attribute_pk === ""){
			$("#error").append("Select attribute from list")
			}
		console.log(test_name)
		if(test_val === ""){
			$("#additional_filters").append("No test selected"); 
		}
		$.get('/kitkat/additional_filters/', {test_name: test_name, request_number:request_number, attribute_pk:attribute_pk}, function(data){

			$("#additional_filters").append(data);
			request_number+=1
		});
});

$("#id_qa_test_def_id").change(function(){
	var test_name = $(this).find(":selected").text()
	$.get('/kitkat/list_filters_for_test/', {test_name: test_name}, function(data){
		lists = data.split("///")
		attrs = lists[0].split("//")
		keys = lists[1].split("//")
		var $attr_select = $("#select_attribute");
		$attr_select.empty();
		$attr_select.append($("<option></option>").attr("value","").text("---------"));
		for(var i=0; i<attrs.length; i++){
			$attr_select.append($("<option></option>").attr("value",keys[i]).text(attrs[i]));
			}
	});

});


});
