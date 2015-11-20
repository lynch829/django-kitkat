$(document).ready(function(){

//make all the input boxes slightly smaller
//$("#table2 input").attr('size', 6)  //didn't work
$("#table2 input").attr('style','width:90px')

//make it impossible for a user to change machine or test type selections
//by removing other options
	var chosen = $("#id_qa_test_def_id").find(":selected").val()
	$("#id_qa_test_def_id > option[value!="+parseInt(chosen)+"]").remove()
	chosen = $("#id_machine_id").find(":selected").val()
	$("#id_machine_id > option[value!="+parseInt(chosen)+"]").remove()

//var list_of_fav_fields = ['f1-1','f1-2','f1-3','f1-4','f1-5']

//add Expected Readings (for choice of electrometer) to table
	//console.log("hello cat")
	console.log($("tr:has(td:has( > #id_f1-1-mean_value))").html())
	$("tr:has(td:has( > #id_f1-1-mean_value))").after("<tr><td align='right'>Expected Reading:</td><td id='expected_6MeV'></td><td id='expected_9MeV'></td><td id='expected_12MeV'></td><td id='expected_15MeV'></td><td id='expected_18MeV'</td></tr>")


$("textarea").change(function(){
	var id = $(this).attr('id')
	astr = "entered_values"
	pref = id.substring(0, id.length-astr.length)
	var k = $(this).val()
	$("#"+pref+"mean_value").val(mean_of_values(k))
});

	$("#id_f_equip-ion_chamber").change(function(){
		var ion_chamber = $(this).find(":selected").text();
		var machine = $("#id_machine_id").find(":selected").text();
		$.get('/kitkat/get_ion_chamber_expected_readings/', {machine_name: machine, ion_chamber_name: ion_chamber}, function(data){
		var vals = data.split("/")
		$("#expected_6MeV").empty()
		expected_reading = vals[0]
		$("#expected_6MeV").append(expected_reading)
		$("#expected_9MeV").empty()
		expected_reading = vals[1]
		$("#expected_9MeV").append(expected_reading)
		$("#expected_12MeV").empty()
		expected_reading = vals[2]
		$("#expected_12MeV").append(expected_reading)
		$("#expected_15MeV").empty()
		expected_reading = vals[3]
		$("#expected_15MeV").append(expected_reading)
		$("#expected_18MeV").empty()
		expected_reading = vals[4]
		$("#expected_18MeV").append(expected_reading)
		});
/*		//changing the selected ion chamber changes other values, so propagate changes from top down
		if( $("input[name=f1-1-mean_value]").val() != ""){
			fix_fav_1_1()
		}
		if( $("input[name=f3-1-mean_value]").val() != ""){
			fix_fav_3_1()
		}		
		if( $("input[name=f1-2-mean_value]").val() != ""){
			fix_fav_1_2()
		}
		if( $("input[name=f3-2-mean_value]").val() != ""){
			fix_fav_3_2()
		}
*/
	});


});


var mean_of_values = function(string){
	var values = string.split('\n');
	var total = 0.0
	var counter = 0
	for(var i=0; i<values.length; i++){
		//need to add case for brackets
		if(!isNaN(values[i]) && values[i].length !=0 ){
			total = total + parseFloat(values[i]);
			counter += 1;
			}
		}
	return total/counter;	
//	return total
}

