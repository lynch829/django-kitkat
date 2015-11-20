"""
views.py
--------

Contains methods to process HTTP GET and POST data:
	- methods provide content for and display web pages
	- methods to assemble data entry forms from QA Test Definitions
	- methods to save data from entry forms into the database
	- methods to respond to Ajax requests sent by javascript $.get calls
"""
#Catherine Bromhead, cathjb@gmail.com, November 19th, 2015

from django.shortcuts import render
from django.views.generic.edit import FormView
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from wbrc.settings import STATIC_URL

from .models import Machine, QATestDefinition, QATestResult, \
	QATestAttributeDefinition, QATestAttributeResult, TestEquipment, \
	TemperaturePressure, FloatValue, FloatAverageValue, \
	QATestInputDefinition, MachineTest, IonChamberAdditionalInfo, BoolValue, \
	IonChamber

from .forms import QATestResultForm, FloatValueForm, \
	SelectMachineAndTestForm, BoolValueForm, FloatAverageValueForm, \
	TestEquipmentForm, TemperaturePressureForm, SearchForm, \
	FloatSearchFilterForm

import calendar


def user_login(request):
	""" 
	process data from log in form, redirect to the home page if the user
	enters a valid username/password combination
	"""
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		#if a valid username/password combination is entered, a user
		#object is returned
		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				 login(request, user)
				 #print "yes we logged in"
				 return HttpResponseRedirect('/kitkat/home')
			else:
				return HttpResponse("Account is inactive")
		else:
			# Bad login details were provided. So we can't log the user in.
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

	else: #not a HTTP POST request, return to login form
		return render(request, 'login.html', {})

@login_required
def user_logout(request):
	"""
	log out user, redirect to login form
	"""
	logout(request)
	# Return user to login form
	return HttpResponseRedirect('/kiktat/login_form')

def login_form(request):
	""" display login form """
	return render_to_response('login.html', \
		context_instance=RequestContext(request))

@login_required
def home(request):
	""" 
	Display the home page with an empty Select Machine and Test Form and
	a table of most recently completed tests
	"""
	template = loader.get_template('home.html')
	select_form = SelectMachineAndTestForm()
	# Generate a list of most recent entries for tests
	tbl = recent_entries_table()
	context = RequestContext(request, {'select_form':select_form, \
		'STATIC_URL':STATIC_URL, 'tbl':tbl})
	return HttpResponse(template.render(context))

def recent_entries_table():
	"""
	List dates of most recently performed QA tests for all valid machine
	and test combinations as defined in Machine Test table
	"""
	machinetest = MachineTest.objects.all()
	tbl = []
	header = ['QA type', 'Machine', 'Most recent test', 'User', 'Link']
	tbl.append(header)
	for mt in list(machinetest):
		row = [mt.qa_test_def_id, mt.machine_id]
		qatr = QATestResult.objects.filter(qa_test_def_id=mt.qa_test_def_id, \
			machine_id=mt.machine_id).order_by('-pub_date')
		if list(qatr) == []:
			row = row + ['--', '--', '--']
		else:
			row = row + [list(qatr)[0].pub_date, list(qatr)[0].user, \
				"<a href='/kitkat/%d/display_entry/'>View entry</a>" \
				% list(qatr)[0].pk]
		tbl.append(row)
	return tbl

def process_machine_and_test_form(request):
	"""
	Input: HTTP POST data from a Select Machine and Test Form

	If valid details have been supplied, the request is redirected to method to 
	display a data entry form for the selected machine and test.
	"""
	context = RequestContext(request)
	if request.method == 'POST':
		# Reconstruct Select form using POST data
		form = SelectMachineAndTestForm(request.POST)
	else:
		form = SelectMachineAndTestForm()
	if form.is_valid():
		t = form.cleaned_data['qa_test_def_id']
	else: #form is not valid, stay on the home page
		return HttpResponseRedirect("/kitkat/home/")

	if str(t) == "Daily Photon Output Test":
		return process_qa_form(request, first_request=True)
	elif str(t) == "Photon Check Calibration":
		return process_qa_form(request, first_request=True)
	elif str(t) == "Electron Check Calibration":
		return process_qa_form(request, first_request=True)
	elif str(t) == "Linac Mechanical Check":
		return linac_mechanical_check_view(request)
	else:
		return HttpResponse("Test definition not found")


def process_qa_form(request, first_request=False):
	"""
	Form display and save method for Daily Photon Output Test, Photon Check
	Calibration and Electron Check Calibration

	Constructs QATestResultForm object from POST data from request.
	Creates all form objects 
	(Float Value Forms, Bool Value Forms, Float Average Value Forms, Test 
	Equipment Forms, Temperature Pressure Forms)
	to assemble the data entry form for the selected 
	test and pass these to the 'qa_testforms.html' template.

	The request contains either:
		- POST data from from a Select Machine and Test Form \
		  (first_request == True) in which case the data entry form is\
		assembled using blank forms
		- POST data from a completed data entry form for validation and saving.\
		If all sub-forms validate, data is saved into the database and user\
		is redirected to the 'display_entry' page for the data submitted.\
		If any form does not validate,  the user is returned to the entry\
		form with error messages
	"""
	# If first_request == True, construct empty forms.  If first_request == 
	# False, construct forms from POST data
	if request.method == 'POST':
		print request.POST
		resultform = QATestResultForm(request.POST)
		if not first_request:
			resultform.user = request.user
		attribute_forms = []  #For all QA Test Attribute Result Forms
		prelim_forms = []	#For Test Equipment and Temperature Pressure Forms
		hidden_forms = []	#For hidden boolean forms
		input_labels = []	#Labels for specific LINAC beam strengths, 
							#if applicable to test
		# save form without committing to access test definition
		saved_resultform = resultform.save(commit=False)
		test_def = saved_resultform.qa_test_def_id
		
		# Create Test Equipment Form if required
		if test_def.test_equip_required:
			if test_def.test_name == "Photon Check Calibration":
				ic_type = "Photon"
			if test_def.test_name == "Electron Check Calibration":
				ic_type = "Electron"
			if first_request:  # Create blank form
				form = TestEquipmentForm(prefix  = "f_equip")
				# Limit ion chamber options to those that can be used for 
				# selected test
				form.limit_ion_chamber_options(ic_type)
			else: # Create form from POST data
				form = TestEquipmentForm(request.POST, prefix  = "f_equip")
				form.limit_ion_chamber_options(ic_type)
			prelim_forms.append(form)
		# Create Temperature Pressure Form if required
		if test_def.temp_pressure_required:
			if first_request:
					form = TemperaturePressureForm(prefix  = "ftp")
			else:
				form = TemperaturePressureForm(request.POST, prefix = "ftp")
			prelim_forms.append(form)
		
		# Get a list of all attributes definitions for the test definition
		attrs = list(QATestAttributeDefinition.objects.filter\
			(qa_test_def_id=test_def).order_by('form_order'))

		# Get all input values (LINAC beam strengths) for the test definition
		# if any exist
		inputs = list(QATestInputDefinition.objects.filter\
			(qa_test_def_id=test_def).order_by('form_order'))

		# Store input labels to pass to template
		if inputs != []:
			for inp in inputs:
				input_labels.append(inp.input_label)
		
		# Arrange a list of lists of form compenents (Float Value Forms, Bool 
		# Value Forms, Float Average Value Forms), n lists of k form objects
		# where n is the number of attributes and k is the number of inputs
		for attr in attrs:
			form_list = []
			if not attr.varied_input: # No input definitions
				form = create_form_component(request=request, first_request=\
					first_request, attribute_type=attr.attribute_type,\
					form_prefix ="f"+str(attr.form_order), label=attr.label,\
					initial_data={'qa_test_attr_def_id':attr})
				form_list.append(form)
			else:
				for inp in inputs:
					form = create_form_component(request=request, \
						first_request=first_request, \
						attribute_type=attr.attribute_type,\
						form_prefix ="f"+str(attr.form_order)+"-"+\
						str(inp.form_order), label=attr.label,\
						initial_data={'qa_test_attr_def_id':attr,\
						'qa_test_input_def_id': inp})
					form_list.append(form)
			if attr.attribute_type != "Hidden Bool Value":
				#print "adding VISIBLE form_list"
				attribute_forms.append(form_list)
			else:
				#print "adding H I D D E N form_list"
				hidden_forms.append(form_list)
		all_valid = False
		# If the request is from a completed form, check forms to see if they
		# are valid.  If not all forms are valid, they are sent back to the
		# template
		if not first_request: #Validation
			all_valid = True
			counter = 1
			# Check all preliminary forms
			for form in prelim_forms:
				if not form.is_valid:
					all_valid = False
			# Check all attribute forms
			for form_list in attribute_forms+hidden_forms:
				for form in form_list:
					if not form.is_valid():
						#print "form "+str(counter)+" does not validate"
						counter+=1
						all_valid = False
					else:
						#print "form "+str(counter)+" DOES validate"
						counter+=1
			if not resultform.is_valid(): #Send everything back
				all_valid = False
		# send the forms to the template if anything is not valid, or if
		# the forms are blank (first_request == True)
		# If a form is to be displayed, define which javascript file
		# is to be used
		if not all_valid:
			scripts = []
			if test_def.test_name == "Electron Check Calibration":
				scripts.append('electron_check_calibration.js')
			if test_def.test_name == "Photon Check Calibration":
				scripts.append('photon_check_calibration.js')
			if test_def.test_name == "Daily Photon Output Test":
				scripts.append('daily_photon_output_test.js')

			return render_to_response('qa_testforms.html', \
				{'resultform':resultform, 'attribute_forms':attribute_forms, \
				'prelim_forms':prelim_forms, 'hidden_forms':hidden_forms, \
				'input_labels':input_labels, 'STATIC_URL':STATIC_URL, \
				'scripts':scripts}, RequestContext(request) )

		if all_valid: # If all forms are valid, save their data to the database
			# Add user to QA Test Result Form
			saved_resultform.user = request.user
			# Save QA Test Result entry
			saved_resultform.save()
			
			# Save Test Equipment Forms and Temperature Pressure Forms
			for form in prelim_forms:
				saved_form = form.save(commit=False)
				# Set foreign key to QA Test Result entry
				saved_form.qa_test_result_id = saved_resultform
				saved_form.save()

			# Save all attribute forms
			for form_list in attribute_forms+hidden_forms:
				for form in form_list:
					saved_form = form.save(commit=False)
					# Set foreign key to QA Test Result entry
					saved_form.qa_test_result_id = saved_resultform
					# Set foreign keys to attribute and input definitions 
					# from hidden components of attribute forms
					if isinstance(saved_form, QATestAttributeResult):
						saved_form.qa_test_attr_def_id = \
							form.cleaned_data['qa_test_attr_def_id']  
						if form.cleaned_data['qa_test_input_def_id']:
							saved_form.qa_test_input_def_id= \
								form.cleaned_data['qa_test_input_def_id']
					saved_form.save()
			
			# Redirect to a display of the data entered into the database
			# from the form			
			return HttpResponseRedirect("/kitkat/%d/display_entry" \
				% saved_resultform.pk  )

"""
create_form_component

Instantiate and return a QA Test Attribute Result Form (Float Value Form,
Bool Value Form or Float Average Value Form) from parameters supplied 
"""
def create_form_component(attribute_type, form_prefix, request, initial_data, \
	label, first_request):
	"""
	Instantiate and return a QA Test Attribute Result Form (Float Value Form,
	Bool Value Form or Float Average Value Form) from parameters supplied 
	"""
	#print "in create_form_component"
	if attribute_type == "Float Value":
		if first_request:
			form = FloatValueForm(prefix=form_prefix, initial=initial_data)
		else:
			form = FloatValueForm(request.POST, prefix=form_prefix)
	elif attribute_type == "Bool Value" \
		or attribute_type == "Hidden Bool Value":
		if first_request:
			form = BoolValueForm(prefix=form_prefix, initial=initial_data)
		else:
			form = BoolValueForm(request.POST, prefix=form_prefix)
		if attribute_type == "Hidden Bool Value":
			form.make_hidden()
	elif attribute_type == "Float Average Value":
		if first_request:
			form = FloatAverageValueForm(prefix=form_prefix, \
				initial=initial_data)
		else:
			form = FloatAverageValueForm(request.POST, prefix=form_prefix)
	form.set_label(label)
	#print "ready to return a form"
	return form

"""
linac_mechanical_check_view
Constructs form for LINAC mechanical check.

TO DO: Modify this method to save POST data from the form as in addition to
as generating the empty form.
"""

def linac_mechanical_check_view(request):
	"""
	Construct data entry form for LINAC mechanical check using test definition

	TO DO: Modify this method to save POST data from the form as in addition to
	as generating the empty form.
	"""	
	prelim_forms = [] 	#for test equipment, temperature and pressure
	attribute_forms = [] #for all QA Test Attribute Result Forms
	scripts = []  #for jquery script associated with test type
	input_labels = []
	#resultform contains machine and test type info
	resultform = QATestResultForm(request.POST)
	if resultform.is_valid(): #only continue if previous step is valid, 
		# TO DO: handle case where input is not valid
		test_def = resultform.cleaned_data['qa_test_def_id']
		# add TestEquipmentForm and TemperaturePressureForm if required
		if test_def.test_equip_required:
			form = TestEquipmentForm(prefix = "f_equip")
			prelim_forms.append(form)
		if test_def.temp_pressure_required:
			form = TemperaturePressureForm(prefix = "ftp")
			prelim_forms.append(form)
	#gather the attributes
	attrs = QATestAttributeDefinition.objects.filter(qa_test_def_id=test_def)
	for attr in attrs:
		# TO DO: Replace form construction below with calls to the
		# create_form_component method
		if attr.attribute_type == "Float Value": 
			form = FloatValueForm(prefix = "f"+str(attr.form_order), \
				initial = {'qa_test_attr_def_id': attr})
			form.set_label(attr.label)
			attribute_forms.append(form)
		if attr.attribute_type == "Bool Value": 
			form = BoolValueForm(prefix = "f"+str(attr.form_order), \
				initial = {'qa_test_attr_def_id': attr})
			form.set_label(attr.label)
			attribute_forms.append(form)
		if attr.attribute_type == "Float Average Value": 
			form = FloatAverageValueForm(prefix = "f"+str(attr.form_order), \
				initial = {'qa_test_attr_def_id': attr})
			form.set_label(attr.label)
			attribute_forms.append(form)
	form_groups = []
	active_group = []
	i = 0
	
	# Create a structure of lists that of attribute forms to pass to the 
	# template in groups.  Attribute labels for this test are often in two 
	# parts, i.e. separated by "##" delimeters, for example attributes with 
	# labels 'label1##label2a' and 'label1##label2b will be displayed as
	# label1		label2a __
	#				label2b __
	# in the template
	while i < (len(attribute_forms)):
		active_group = [attribute_forms[i]]
		label = attribute_forms[i].fields['value'].label.split("##")
		more_in_group = True
		while more_in_group and i < len(attribute_forms)-1:
			labelnext = attribute_forms[i+1].fields['value'].label.split("##")
			if label[0] == labelnext[0]:
				i+=1
				active_group.append(attribute_forms[i])
			else:
				more_in_group = False
		form_groups.append(active_group)
		i+=1
	formatted_groups = []
	for form_group in form_groups: 	#this works with max depth 2 
									#(ok for linac mechanical)
		listo = []
		label = form_group[0].fields['value'].label.split("##")
		#print label
		if len(label) == 2:
			listo.append(label[0])
			formlist = []
			for form in form_group:
				label1 = form.fields['value'].label.split("##")
				#print label1
				form.set_label(label1[1])
				formlist.append(form)
			listo.append(formlist)
		elif len(label) == 1:
			for form in form_group:
				form.set_label(label[0])
			listo.append(form)
		formatted_groups.append(listo)
		#print "formatted groups"
		#print formatted_groups
	
	# FORM INSTRUCTION FOR LINAC MECHANICAL CHECK
	# These are instructions to be displayed on the form that are not specific
	# to any one QA Test Attribute Definition entry
	# TO DO: Incorporate these into QA Test Attribute Definitions as 
	# a new category to attribute types, 'form instruction'
	inst1 = "Set up the 'Beam Check Device' (BCD) with 10cm x 10cm field \
		size, collimator and gantry at 0&deg and SSD 100cm using the \
		mechanical pointer"
	inst2 = "Rotate gantry to 180&deg and set isocentre check part of BCD \
		with mechanical pointer in position"
						
	return render_to_response('linacmechanicalcheck.html', \
		{'resultform':resultform, 'inst1':inst1, \
		'formatted_groups':formatted_groups, 'STATIC_URL':STATIC_URL, \
		'scripts':scripts, 'prelim_forms':prelim_forms, \
		'input_labels':input_labels, 'range2':[0,1]}, RequestContext(request) )

@login_required
def display_entry(request, test_result_id):
	"""
	display_entry
	Create a HTTPResponse object containing all data for a QA Test Result
	entry with a given primary key
	"""
	# Select QA Test Result with requested primary key
	Result = QATestResult.objects.get(pk=test_result_id)

	varied_inputs = False
	TestDef = Result.qa_test_def_id
	input_labels = []
	attrs = []
	# Collect all attributes that have foreign keys to this QA Test Result
	if TestDef.variable_input:
		varied_inputs = True
		inputs = QATestInputDefinition.objects.filter\
			(qa_test_def_id=TestDef).order_by('form_order')
		
		for inp in inputs:
			attributes = QATestAttributeResult.objects.filter\
				(qa_test_result_id=Result, qa_test_input_def_id=inp)
			attributes = sorted(attributes, \
				key = lambda attr: attr.qa_test_attr_def_id.form_order)

			attrs.append(attributes)			
			input_labels.append(inp.input_label)
	else:
		attributes = \
			QATestAttributeResult.objects.filter(qa_test_result_id=Result)
		attributes = sorted(attributes, \
			key = lambda attr: attr.qa_test_attr_def_id.form_order)
		attrs.append(attributes)
	#print "RUNNING"
	
	Testequip = TestEquipment.objects.filter(qa_test_result_id=Result)
	TempPressure = TemperaturePressure.objects.filter(qa_test_result_id=Result)

	# Write HTTPResponse object with all data for the QA Test Result and 
	# associated entries
	response = HttpResponse()
	response.write("<p>%s : %s</p>" % ("Date", Result.pub_date) )
	response.write("<p>%s : %s</p>" % ("User", Result.user) )
	response.write("<p>%s : %s</p>" % ("QA test", str(Result.qa_test_def_id)) )
	response.write("<p>%s : %s</p>" % ("Machine", str(Result.machine_id)) )
	if not len(Testequip) == 0:
		response.write("<p>%s : %s</p>" % \
			("Electrometer", str(Testequip[0].electrometer)) )
		response.write("<p>%s : %s</p>" % \
			("Ion Chamber", str(Testequip[0].ion_chamber)) )
	if not len(TempPressure) == 0:
		response.write("<p>%s : %.2f</p>" % \
			("Temperature", TempPressure[0].temperature) )
		response.write("<p>%s : %.2f</p>" % \
			("Pressure", TempPressure[0].pressure) )
	index = 0
	for attr_list in attrs:
		if TestDef.variable_input:
			response.write("<p>Readings for %s beam:</p>" % input_labels[index])
		print "ATTR LIST",attr_list
		for attribute in attr_list:
			if attribute.qa_test_attr_def_id.attribute_type == "Float Value":
				floatvalue = FloatValue.objects.get(pk=attribute.pk)
				response.write("<p>%s : %.2f</p>" % \
					(floatvalue.qa_test_attr_def_id.label, floatvalue.value) )
			if attribute.qa_test_attr_def_id.attribute_type == \
				"Float Average Value":
				pass
				floataveragevalue = \
					FloatAverageValue.objects.get(pk=attribute.pk)
				response.write("<p>%s : %s</p>" % \
					(floataveragevalue.qa_test_attr_def_id.label, \
					floataveragevalue.entered_values) )
				response.write("<p>%s : %.2f</p>" % \
					("Mean", floataveragevalue.mean_value) )
			if attribute.qa_test_attr_def_id.attribute_type == "Bool Value" \
				or attribute.qa_test_attr_def_id.attribute_type == \
				"Hidden Bool Value":
				boolvalue = BoolValue.objects.get(pk=attribute.pk)
				response.write("<p>%s : %s</p>" % \
					(boolvalue.qa_test_attr_def_id.label, boolvalue.value) )
		index+=1
	# Add the form comment if it exists
	if Result.comment != "":
		response.write("<p>%s : %s</p>" % ("Comment", Result.comment) )
	# Add Home link
	response.write("<p><a href=\'/kitkat/home\'>Home</a></p>")
	# Add link to past entries for this test and machine
	response.write("<p><a href=\'/kitkat/%d/%d/past_results\'>\
	Past entries for %s on %s</a></p>" % (Result.qa_test_def_id.pk, \
	Result.machine_id.pk, str(Result.qa_test_def_id), str(Result.machine_id) ))
	
	return response

@login_required
def past_results(request, qa_test_def, machine):
	"""
	Display a list of links to data from QA Test Result entries specific
	to a given machine and given test
	"""
	machine = int(machine)
	qa_test_def = int(qa_test_def)
	result_set = QATestResult.objects.all()
	print "the result set is this big: %d" % len(result_set)
	if machine != 0:
		result_set = result_set.filter(machine_id=machine)
	print "the result set is this big: %d" % len(result_set)
	if qa_test_def != 0:
		result_set = result_set.filter(qa_test_def_id=qa_test_def)
	print "the result set is this big: %d" % len(result_set)
	result_set = result_set.order_by('-pub_date')
	response = HttpResponse()
	for result in result_set:
		response.write("<p><a href=\'/kitkat/%d/display_entry\'>%s</a></p>" % \
			(result.pk, str(result)) )
	response.write("<a href=\'/kitkat/home\'>Home</a>")
	return response


def search(request):
	"""
	Display search.html page
	"""
	form = SearchForm()
	return render_to_response("searchform.html",{'form':form, \
		'STATIC_URL':STATIC_URL} ,RequestContext(request))

def searchdb(request):
	"""
	Process Search Form and return results as a HTTPResponse object
	
	First filter all test results by parameters defined in Search Form,
	then apply additional filters
	"""
	if request.method == 'POST':
		print request.POST.items()
		# Find 'additional filter' forms in POST data
		filters = [x[0:len(x)-6] for x in request.POST.keys() \
			if x[0:2] == "sf" and x[len(x)-6:len(x)] == "-label"]
		#print "filters", filters
		searchform = SearchForm(request.POST)
		test_selected = False
		if searchform.is_valid():   #which it ought to be, 
									#because all fields are optional
			qset = QATestResult.objects.all()
			print "qset length",len(list(qset))

			# Filter data based on fields defined in the search form
			if searchform.cleaned_data['qa_test_def_id']:
				test_selected = True
				qset = qset.filter(qa_test_def_id=\
					searchform.cleaned_data['qa_test_def_id'])
				#print "qset length",len(list(qset))
			if searchform.cleaned_data['machine_id']:
				qset = qset.filter(machine_id = \
					searchform.cleaned_data['machine_id'])
				#print "qset length",len(list(qset))
			if searchform.cleaned_data['user_id']:
				qset = qset.filter(user = searchform.cleaned_data['user_id'])
				#print "qset length",len(list(qset))
			if searchform.cleaned_data['date_from']:
				qset = qset.filter\
					(pub_date__gte=searchform.cleaned_data['date_from'])
				#print "qset length",len(list(qset))
			if searchform.cleaned_data['date_to']:
				qset = qset.filter\
					(pub_date__lte=searchform.cleaned_data['date_to'])
				#print "qset length",len(list(qset))

			if test_selected: #Filter on attributes only if test is defined
				attr_set = QATestAttributeDefinition.objects.filter\
					(qa_test_def_id=searchform.cleaned_data['qa_test_def_id'])
			if list(qset) == []:
				return HttpResponse("No results for search")

			for sfilter in filters:
				label = request.POST[sfilter+"-label"]

				attr = attr_set.get(label=label)
				print "filtering on this attribute", attr
				if attr.attribute_type == "Float Value": 
					filter_form = FloatSearchFilterForm(request.POST)
					rset = FloatValue.objects.filter\
						(qa_test_result_id__in = qset)
					#print rset
					operator = request.POST[sfilter+"-operator"]
					value = float(request.POST[sfilter+"-value"])
					if operator == "GREATER THAN":
						rset = rset.filter(value__gte = value)
					if operator == "LESS THAN":
						rset = rset.filter(value__lte = value)
					pks = []
					for r in list(rset):
						pks.append(r.qa_test_result_id.pk)
					qset = qset.filter(pk__in = pks)
					print "qset length",len(list(qset))

			if list(qset) == []:
				return HttpResponse("No results for search")
			else:
				response = HttpResponse()
				response.write("<style media=\"screen\" type=\"text/css\">\n\
						#table1, #table1 td {\n\tpadding: 5px;\n}</style>")
				response.write("<table id=\"table1\">")
				response.write("<tr>")
				response.write("<td>Test type</td>"+\
					"<td>Machine</td><td>Date</td><td>User</td>")
				if test_selected:
					inputs = list(QATestInputDefinition.objects.filter\
						(qa_test_def_id=\
						searchform.cleaned_data['qa_test_def_id'])	)
					attrs = QATestAttributeDefinition.objects.filter\
						(qa_test_def_id=\
						searchform.cleaned_data['qa_test_def_id'])
#					attribute_definitions = []
					for attr in attrs:
						if attr.varied_input:
							for inp in inputs:
								if attr.attribute_type == "Float Value":
									response.write("<td>"+inp.input_label+\
										";"+attr.label+"</td>")
								if attr.attribute_type == "Float Average Value":
									response.write("<td>"+inp.input_label+";"+\
									attr.label+"</td><td>"+inp.input_label+\
									";"+attr.label+" (mean)</td>")
						else:
							if attr.attribute_type == "Float Value":
								response.write("<td>"+attr.label+"</td>")
							if attr.attribute_type == "Float Average Value":
								response.write("<td>"+attr.label+" (mean)</td>")
				response.write("</tr>")
				for q in list(qset):
					response.write("<tr><td>"+str(q.qa_test_def_id)+\
					"</td><td>"+str(q.machine_id)+"</td><td>"\
					+str(q.pub_date.day)+"/"+str(q.pub_date.month)+"/"\
					+str(q.pub_date.year)+"</td><td>"+str(q.user)+"</td>")
					if test_selected:
						attr_results = QATestAttributeResult.objects.filter\
							(qa_test_result_id=q)
						for attr in attrs:
							if attr.varied_input:
								for inp in inputs:
									qatar = attr_results.get\
										(qa_test_input_def_id=\
										inp,qa_test_attr_def_id=attr)
									#print qatar
									if attr.attribute_type == "Float Value":
										#print "fvf"
										fvf = FloatValue.objects.get\
											(pk=qatar.pk)
										response.write\
											("<td>"+str(fvf.value)+"</td>")
									if attr.attribute_type == \
										"Float Average Value":
										#print "favf"
										favf = FloatAverageValue.objects.get\
											(pk=qatar.pk)
										response.write("<td>"+\
											favf.entered_values+"</td><td>"+\
											str(favf.mean_value)+"</td>")
					response.write("</tr>")
				response.write("</table>")
				response.write("<p><a href='/kitkat/search/'>"\
					+"Back to search page</a></p>")
				response.write("<p><a href=\'/kitkat/home\'>Home</a></p>")
				
			return response
		else:
			return render_to_response("searchform.html",{'form':searchform, \
				'STATIC_URL':STATIC_URL} ,RequestContext(request))

				
###########################################
#		METHODS FOR AJAX CALLS            #
###########################################

def additional_filters(request):
	"""
	Construct additional filter form element for search page
	"""
	#print "F1"
	if request.method == 'GET':
		#print "F2"
		qa_test_name = request.GET['test_name']
		request_number = request.GET['request_number']
		attribute_pk = int(request.GET['attribute_pk'])
		#print "F3"
		
		test_object = QATestDefinition.objects.get(test_name=qa_test_name)
		qset = QATestAttributeDefinition.objects.filter\
			(qa_test_def_id=test_object)
		form_label_choices = [("", "-------")]
		for q in list(qset):
			form_label_choices.append( (q.label, q.label) ) 
		#print "F4"
		attr_choice = QATestAttributeDefinition.objects.get(pk=attribute_pk)
		form = FloatSearchFilterForm(prefix="sf"+request_number)
		#print "F5"
		form.set_label_choices(form_label_choices)
		#print "F6"
		form.initial = {'label':attr_choice.label}
		#print "F7"
		#print "about to return, this is probably an illegal move though"
		return render_to_response("filters.html", \
			{'form':form}, RequestContext(request))

def list_filters_for_test(request):
	"""
	Find QA Test Attribute Definitions for a QA Test Definition that may
	be used to filter search results
	"""
	if request.method == 'GET':
		qa_test_name = request.GET['test_name']
		test_object = QATestDefinition.objects.get(test_name=qa_test_name)
		qset = QATestAttributeDefinition.objects.filter\
			(qa_test_def_id=test_object)
		response_str = ""
		primary_keys = ""
		counter = 0
		for q in list(qset):
			if counter > 0:
				response_str+="//"
			if q.attribute_type == "Float Average Value":
				response_str+=q.label+" (mean)"
			else:
				response_str+=q.label
			primary_keys+=str(q.pk)
			counter+=1
		response_str = response_str+"///"+primary_keys
		return HttpResponse(response_str)


@login_required
def recent_results_daily_photon_output_test(request):
	"""
	Return 5 most recent entries for the Daily Photon Output Test along with
	entry dates
	"""
	num_recent = 5
	recent_readings = []
	reading_times = []
	if request.method == 'GET':
		machine_name = request.GET['machine_name']
	#print "flag 1"
	test_def = QATestDefinition.objects.get(test_name="Daily Photon Output Test")
	#print "flag 2"
	result_set = QATestResult.objects.filter(qa_test_def_id=test_def)
	#print "flag 3"
	machine = Machine.objects.get(machine_name=machine_name)
	result_set = result_set.filter(machine_id=machine).order_by('-pub_date')
	for i in range(num_recent):
		attr = FloatValue.objects.filter(qa_test_result_id=result_set[i].pk)
		#print len(attr)
		if(len(attr) == 1):
			recent_readings.append(attr[0].value)
			reading_times.append(calendar.timegm\
				(result_set[i].pub_date.timetuple()) * 1000)
	#print "flag 4"
	data = str(reading_times[0]) + " " + str(recent_readings[0])
	for i in range(1, len(recent_readings)):
		data +="/" + str(reading_times[i]) + " " + str(recent_readings[i])
	return HttpResponse(data)

def list_machines_for_test(request):
	"""
	Return a list of applicable machines for a given QA Test Definition
	"""
	#print "F1"
	if request.method == 'GET':
		qa_test_name = request.GET['test_name']
	#print "F2"
	test = QATestDefinition.objects.get(test_name=qa_test_name)
	#print "F3"
	qset = MachineTest.objects.filter(qa_test_def_id=test)
	#print "F4"
	return_values = ""
	primary_keys = ""
	counter = 0
	for q in list(qset):
		if counter > 0:
			return_values+="##"
			primary_keys+="##"
		return_values+=q.machine_id.machine_name
		primary_keys+=str(q.machine_id.pk)
		counter+=1
	return_values = return_values+"/"+primary_keys
	return HttpResponse(return_values)

def get_dpot_bounds(request):
	"""
	Retrieve upper and lower bounds for Daily Photon Output Test
	"""
	if request.method == 'GET':
		test_name = "Daily Photon Output Test"
		machine_name = request.GET['machine_name']
		machine = Machine.objects.get(machine_name=machine_name)
		#print machine
		#print IonChamberAdditionalInfo.objects.all()
		info = IonChamberAdditionalInfo.objects.get(machine_id=machine, \
			daily_photon_lower_bound__isnull = False)
		#print info
		return HttpResponse(str(info.daily_photon_lower_bound)+\
			"/"+str(info.daily_photon_upper_bound))

def get_ion_chamber_expected_readings(request):
	"""
	Get expected readings from Ion Chamber Additional Info table once
	an Ion Chamber has been selected in an entry form
	"""
	if request.method == 'GET':
		ion_chamber_name = request.GET['ion_chamber_name']
		machine_name = request.GET['machine_name']
		#print "F1"
		machine = Machine.objects.get(machine_name=\
			machine_name,is_visible=True)
		ion_chamber = IonChamber.objects.get\
			(ion_chamber_name=ion_chamber_name,is_visible=True)
		#print "F2"
		expected_readings = ""
		if ion_chamber.ion_chamber_type == "Photon":
			labels = ("6MV", "18MV")
		if ion_chamber.ion_chamber_type == "Electron":
			labels = ("6MeV", "9MeV", "12MeV", "15MeV", "18MeV")
		counter = 0
		for label in labels:
			#print "F3"
			info = IonChamberAdditionalInfo.objects.get(ion_chamber_id=\
				ion_chamber,input_label=label,machine_id=machine)
			#print "F4"
			expected_readings+=str(info.expected_reading)
			if counter < len(labels)-1:
				expected_readings+="/"
			counter+=1
			print "F5"
		return HttpResponse(expected_readings)

def get_ratio_bounds(request):
	"""
	Get upper and lower limits for DCF Ratio from Ion Chamber Additional Info 
	table once an Ion Chamber and Machine have been selected in an entry form
	"""
	if request.method == 'GET':
		ion_chamber_name = request.GET['ion_chamber_name']
		machine_name = request.GET['machine_name']
		return_string = ""
		#print "F1"
		machine = Machine.objects.get(machine_name=\
			machine_name,is_visible=True)
		ion_chamber = IonChamber.objects.get(ion_chamber_name=\
			ion_chamber_name,is_visible=True)
		#print "F2"
		labels = ("6MV", "18MV")
		counter = 0
		for label in labels:
			info = IonChamberAdditionalInfo.objects.get(ion_chamber_id=\
				ion_chamber,input_label=label,machine_id=machine)
			return_string+=str(info.energy_over_output_ratio_lower_bound)+\
				"/"+str(info.energy_over_output_ratio_upper_bound)
			if counter < len(labels)-1:
				return_string+="##"
			counter+=1
		#print "F3"
		return HttpResponse(return_string)

