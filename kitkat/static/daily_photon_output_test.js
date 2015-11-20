
$(document).ready(function(){

//make it impossible for a user to change machine or test type selections
//by removing other options
	var chosen = $("#id_qa_test_def_id").find(":selected").val()
	$("#id_qa_test_def_id > option[value!="+parseInt(chosen)+"]").remove()
	chosen = $("#id_machine_id").find(":selected").val()
	$("#id_machine_id > option[value!="+parseInt(chosen)+"]").remove()

//plot data from previous entries
//need to find recent entries for current machine
	var machine = $("#id_machine_id").find(":selected").text();
	console.log(machine)
//append plot area to the end of the page
	$("html").append("<div id='flot' style='width:700px;height:300px'></div>")
//ajax call to method in views
	$.get('/kitkat/recent_results_daily_photon_output_test/', {machine_name: machine}, function(data){
		console.log("about to log the data")
		console.log(data)
		//plot data from 5 most recent entries
		var plot_data = []
		var tix = []
		var points = data.split("/")
		for(var j=0; j<points.length; j++){
			var sep = (points[j]).split(" ")
			//plot_data.push([parseInt(sep[0]), parseFloat(sep[1])])
			plot_data.push(parseFloat(sep[1]))
			tix.push(parseInt(sep[0]))
			}
		var myDates = []
		for(var i=0; i< tix.length; i++){
			var date = new Date(tix[i])
			myDates.push(date.toDateString())
			}
		var tixmax = tix[tix.length-1]
		console.log("tixmax")
		console.log(tixmax)
		var tixmin = tix[0]
		console.log("tix length")
		console.log(tix.length)
		for(var i=1; i<tix.length-1;i++){
			tix[i] = tixmin + i*(tixmax-tixmin)/(tix.length-1);
			console.log(tixmax-tixmin)
			console.log((tixmax-tixmin)/(tix.length-1))
			}
		var newtix = []
		var new_plot_data = []
		for(var i=0; i< tix.length; i++){
			newtix.push([tix[i], myDates[i]])
			new_plot_data.push([tix[i], plot_data[i]])
			}
		console.log(newtix)		
		var xmax = tixmax - (tixmin-tixmax)/20
		var xmin = tixmin + (tixmin-tixmax)/20
		console.log("xmax xmin")
		console.log(xmax)
		console.log(xmin)
		console.log("ticks")
		console.log(tix)
		console.log(plot_data[0])
		var options = {
			xaxis: { mode: "time", timeformat: "%a %d/%m/%y", ticks: newtix, max: xmin, min: xmax}, 
			//xaxis: { mode: "time", timeformat: "%a %d/%m/%y", ticks: [1,2,3,4,5]}, 
			series: {
    				lines: {
        				show: true,
        				lineWidth: 2,
					color: "red"
        				//fill: true,
        				//fillColor: "red"
    				}
			}
		};

		$.plot("#flot", [{data:new_plot_data, color:"red", hoverable:true}], options);

	});

//	console.log("in the script");
//	console.log("TESTING--------------------------")
//	console.log( $("td:has( > #id_f1-1-value)" ).html()  )

//attach a tag to put pass/fail info from entered value

// 	below is original 
//	$("td:has( > #id_f1-1-value)" ).append("<span id='pass_fail'>&nbsp</span>")

//hopefully this improves it:  Only for TU1 so far...
$("#table2").append("<tr><td></td><td id='pass_fail'>&nbsp</td></tr>")



//	console.log($("pass_fail")
//  $("p").append(" Yes, a frog")
//	$("input[name=f1-value]").change(function(){
	$("input[name=f1-1-value]").change(function(){
		console.log("...")
//		$("#testing").append(".....")
   		var toAdd = $("input[name=f1-1-value]").val();
		console.log(toAdd)

//   var toAdd = $("input[name=f1-value]").val();
//   $("form").append("<p col='red'>hi!!! " + toAdd +"</p")
//	$("#pass").empty()
//	$("#pass").append(toAdd)
	$.get('/kitkat/get_dpot_bounds/', {machine_name: machine}, function(data){
		var bounds = data.split("/");
		var daily_photon_test_lower_bound = bounds[0]
		var daily_photon_test_upper_bound = bounds[1]
	
	if( (toAdd >= daily_photon_test_lower_bound) && (toAdd <= daily_photon_test_upper_bound) ){
//		$("p:has( > label[for=id_f1-value])").append("<p><font color='green'>OK</font></p>");
//		console.log($("p:has( > label[for=id_f1-value])").html())
//		$("#testing").append("<p><font color='green'>OK</font></p>");
		$("#pass_fail").empty()
		$("#pass_fail").append("<font color='green'>OK</font>")
		//$("input[name=f2-1-value]").prop('checked', true);
		$("input[name=f2-1-value]").val('1'); //boolean field, 1 for TRUE
	}
	else{
/*		$("p:has( > label[for=id_f1-value])").append("<p><font color='red'>Outside of test bounds (" + daily_photon_test_lower_bound + 
	"," + daily_photon_test_upper_bound + ")</font></p>"); */
		$("input[name=f2-1-value]").val('0'); //boolean field, 0 for FALSE
		$("#pass_fail").empty()
		$("#pass_fail").append("<font color='red'>Outside test bounds (" + daily_photon_test_lower_bound + 
	"," + daily_photon_test_upper_bound + ")</font>")
	}
});
	
	});
//some code to test drop down menu:
	$("select").change(function(){
		console.log($("select").html())
		console.log($("form").html())

});
});

