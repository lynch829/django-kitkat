/*var expected_vals_6MV = 
	{	'2571/2044':2.522,
		'2581/769':1.972,
		'2581/875':1.976,
		'2581/1120':2.030  //need to move this logic
	}

var expected_vals_18MV = 
	{	'2571/2044':2.531,
		'2581/769':1.997,
		'2581/875':2.004,
		'2581/1120':2.056  //need to move this logic
	}
*/
var expected_reading_6 = null
var expected_reading_18 = null
var dec_digits = 4
var bounds_6MV_lower = null
var bounds_6MV_upper = null
var bounds_18MV_lower = null
var bounds_18MV_upper = null


$(document).ready(function(){
console.log("not broken yet!")

//make it impossible for a user to change machine or test type selections
//by removing other options
	var chosen = $("#id_qa_test_def_id").find(":selected").val()
	$("#id_qa_test_def_id > option[value!="+parseInt(chosen)+"]").remove()
	chosen = $("#id_machine_id").find(":selected").val()
	$("#id_machine_id > option[value!="+parseInt(chosen)+"]").remove()

//make all the input boxes slightly smaller
//$("#table2 input").attr('size', 6)  //didn't work
$("#table2 input").attr('style','width:90px')

//make calculated fields read-only
//	$("input[name=f1-1-mean_value]").val('122')
	console.log("this here!!!");
	$("input[name=f1-1-mean_value]").attr('readonly', true)
	$("input[name=f1-2-mean_value]").attr('readonly', true)
	$("input[name=f3-1-mean_value]").attr('readonly', true)
	$("input[name=f3-2-mean_value]").attr('readonly', true)
	$("input[name=f2-1-value]").attr('readonly', true)
	$("input[name=f2-2-value]").attr('readonly', true)
	$("input[name=f4-1-value]").attr('readonly', true)
	$("input[name=f4-2-value]").attr('readonly', true)

//add Expected Readings (for choice of electrometer) to table
	console.log("hello cat")
	console.log($("tr:has(td:has( > #id_f1-1-mean_value))").html())
	$("tr:has(td:has( > #id_f1-1-mean_value))").after("<tr><td align='right'>Expected Reading:</td><td id='expected_6MV'></td><td id='expected_18MV'</td></tr>")

//add Ratio limits underneath Ratio
	$("tr:has(td:has( > #id_f4-1-value))").after("<tr><td align='right'>Ratio Limits:</td><td id='bounds_6MV'></td><td id='bounds_18MV'></td></tr>")

//add pass/fail for DCF
	$("tr:has(td:has( > #id_f2-1-value))").after("<tr id='dcf_pass'><td>&nbsp</td><td id='dcf_pass-2-1'></td><td id='dcf_pass-2-2'></td></tr>")

//add pass/fail for DCF
	$("tr:has(td:has( > #id_f4-1-value))").after("<tr id='ratio_pass'><td>&nbsp</td><td id='ratio_pass-4-1'></td><td id='ratio_pass-4-2'></td></tr>")

//<deprecated>	$("p:has( > label[for=id_f1-mean_value])").append("<p>Expected Reading: <span id='expected_reading'></span></p>")

//calculate average values from float average value forms and insert calculated values in mean_value field

//could come back and fix this so that all four float-average-values are calculated by the same script

	$("textarea[id=id_f1-1-entered_values]").change(function(){
		fix_fav_1_1()
		if( $("input[name=f3-1-mean_value]").val() != ""){
			fix_fav_3_1()
		}
	});

	$("textarea[id=id_f1-2-entered_values]").change(function(){
		fix_fav_1_2()
		if( $("input[name=f3-2-mean_value]").val() != ""){
			fix_fav_3_2()
		}
	});
	
	$("textarea[id=id_f3-1-entered_values]").change(function(){
		fix_fav_3_1()
	});

	$("textarea[id=id_f3-2-entered_values]").change(function(){
		fix_fav_3_2()	
	});


	fix_fav_1_1 = function(){	
		var k = $("textarea[id=id_f1-1-entered_values]").val();
		$("input[name=f1-1-mean_value]").val( mean_of_values(k).toFixed(dec_digits) );
		var dcf = (mean_of_values(k)/expected_reading_6)
		$("input[name=f2-1-value]").val( dcf.toFixed(dec_digits));
		if(dcf >=1){
			var plusminus = "+"
			}
		else{
			var plusminus = ""
			}
		if(dcf < 1.02 && dcf > 0.98){			
			$("#dcf_pass-2-1").empty()
			$("#dcf_pass-2-1").append("<font color='green'>"+plusminus+(dcf*100-100).toFixed(2)+"%</font>")
			}
		else{			
			$("#dcf_pass-2-1").empty()
			$("#dcf_pass-2-1").append("<font color='red'>"+plusminus+(dcf*100-100).toFixed(2)+"%</font>")
			}

	}

	fix_fav_1_2 = function(){
		var k = $("textarea[id=id_f1-2-entered_values]").val();
		$("input[name=f1-2-mean_value]").val(mean_of_values(k).toFixed(dec_digits));
		var dcf = (mean_of_values(k)/expected_reading_18)
		$("input[name=f2-2-value]").val( dcf.toFixed(dec_digits) );
		if(dcf >=1){
			var plusminus = "+"
			}
		else{
			var plusminus = ""
			}
		if(dcf < 1.02 && dcf > 0.98){			
			$("#dcf_pass-2-2").empty()
			$("#dcf_pass-2-2").append("<font color='green'>"+plusminus+(dcf*100-100).toFixed(2)+"%</font>")
			}
		else{			
			$("#dcf_pass-2-2").empty()
			$("#dcf_pass-2-2").append("<font color='red'>"+plusminus+(dcf*100-100).toFixed(2)+"%</font>")
			}

	}

	fix_fav_3_1 = function(){
		var k = $("textarea[id=id_f3-1-entered_values]").val()
		var mean = mean_of_values(k)
		$("input[name=f3-1-mean_value]").val(mean.toFixed(dec_digits))
		var g = mean/parseFloat($("input[name=f1-1-mean_value]").val())
		$("input[name=f4-1-value]").val(g.toFixed(dec_digits))
		if(g >= bounds_6MV_lower && g <= bounds_6MV_upper){
			$("#ratio_pass-4-1").empty()
			$("#ratio_pass-4-1").append("<font color='green'>OK</font>")
			}
		else{
			if(g < bounds_6MV_lower){
				$("#ratio_pass-4-1").empty()
				$("#ratio_pass-4-1").append("<font color='red'>&lt"+bounds_6MV_lower+"</font>")
				}
			else{
				$("#ratio_pass-4-1").empty()
				$("#ratio_pass-4-1").append("<font color='red'>&gt"+bounds_6MV_upper+"</font>")
				}
			}

	}

	fix_fav_3_2 = function(){
		var k = $("textarea[id=id_f3-2-entered_values]").val()
		var mean = mean_of_values(k)
		$("input[name=f3-2-mean_value]").val(mean.toFixed(dec_digits))
		var g = mean/parseFloat($("input[name=f1-2-mean_value]").val())
		$("input[name=f4-2-value]").val(g.toFixed(dec_digits))
		if(g >= bounds_18MV_lower && g <= bounds_18MV_upper){
			$("#ratio_pass-4-2").empty()
			$("#ratio_pass-4-2").append("<font color='green'>OK</font>")
			}
		else{
			if(g < bounds_18MV_lower){
				$("#ratio_pass-4-2").empty()
				$("#ratio_pass-4-2").append("<font color='red'>&lt"+bounds_18MV_lower+"</font>")
				}
			else{
				$("#ratio_pass-4-2").empty()
				$("#ratio_pass-4-2").append("<font color='red'>&gt"+bounds_18MV_upper+"</font>")
				}
			}

	}
	console.log("...   ....   ...")
/* already blanked	$("input[name=f3-mean_value]").change(function(){
		var g = parseFloat($("input[name=f3-mean_value]").val())/parseFloat($("input[name=f1-mean_value]").val())
		console.log(g)
		$("input[name=f4-value]").val(g)
});
*/
	$("#id_f_equip-ion_chamber").change(function(){
		console.log("ION CHAMBER SELECTION HAS CHANGED")
		var ion_chamber = $(this).find(":selected").text();
		var machine = $("#id_machine_id").find(":selected").text();
		$.get('/kitkat/get_ion_chamber_expected_readings/', {machine_name: machine, ion_chamber_name: ion_chamber}, function(data){
		var vals = data.split("/")
		$("#expected_6MV").empty()
		expected_reading_6 = vals[0]
		$("#expected_6MV").append(expected_reading_6)
		$("#expected_18MV").empty()
		expected_reading_18 = vals[1]
		$("#expected_18MV").append(expected_reading_18)
		});
		//add Ratio Limits under Ratio.
		$.get('/kitkat/get_ratio_bounds/', {machine_name: machine, ion_chamber_name:ion_chamber}, function(data){
		console.log(data)
		var bounds = data.split("##")
		bounds_6MV_lower = parseFloat(bounds[0].split("/")[0])
		bounds_6MV_upper = parseFloat(bounds[0].split("/")[1])
		bounds_18MV_lower = parseFloat(bounds[1].split("/")[0])
		bounds_18MV_upper = parseFloat(bounds[1].split("/")[1])
		console.log("setting the bounds")
		console.log(bounds_6MV_lower)
		console.log(bounds_6MV_upper)

		$("#bounds_6MV").empty()
		$("#bounds_6MV").append(bounds_6MV_lower+"-"+bounds_6MV_upper)
		$("#bounds_18MV").empty()
		$("#bounds_18MV").append(bounds_18MV_lower+"-"+bounds_18MV_upper)
		});

		//changing the selected ion chamber changes other values, so propagate changes from top down
		if( $("input[name=f1-1-mean_value]").text() != ""){
			fix_fav_1_1()
		}
		if( $("input[name=f3-1-mean_value]").text() != ""){
			fix_fav_3_1()
		}		
		if( $("input[name=f1-2-mean_value]").text() != ""){
			fix_fav_1_2()
		}
		if( $("input[name=f3-2-mean_value]").text() != ""){
			fix_fav_3_2()
		}
	});
/*//Check that the DCF is within bounds for both 6MV and 18MV
$("input[name=f2-1-value]").change(function(){
	if($(this).val() <= bounds_6MV_upper & $(this).val() >= bounds_6MV_lower){
		$("input[name=f5-1-value]").prop('checked', true);
	}
 });
*/
/*
$("input[name=f2-1-value]").change(function(){
	console.log("+++++")
	$("#dcf_pass-2-1").append("hello")
});
*/

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

