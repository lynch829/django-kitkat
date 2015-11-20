"""
models.py
---------

Contains definitions of all tables in the database as Python objects
"""
#Catherine Bromhead, cathjb@gmail.com, November 19th, 2015

from django.db import models
from django.contrib.auth.models import User

"""
Aspects of this that need attention:
Variable input in QATD needs to be removed
QATAD attribute_type needs to be strict choice of ATTR_TYPE_CHOICES
QATID input_label needs to be related to beams, somehow
QATAD label1 label2 etc
Need to check that comment_max_length for QATR is enforced
String method for QATR is a bit strange, could define str for pub_date itself?
"""

###MAXIMUM LENGTHS FOR CHAR FIELDS:

#Machine
machine_serial_number_max_length = 30
machine_name_max_length = 20
machine_type_max_length = 30
machine_model_max_length = 30

#Electrometer
electrometer_name_max_length = 20
electrometer_manufacturer_max_length = 50
electrometer_model_max_length = 50

#IonChamber
ion_chamber_name_max_length = 30
ion_chamber_serial_number_max_length = 30
ion_chamber_manufacturer_max_length = 50
ion_chamber_model_max_length = 50
ion_chamber_calibration_lab_max_length = 50
ion_chamber_type_max_length = 20

#QATestDefinition
qa_test_name_max_length = 50
qa_test_frequency_max_length = 20

#QATestInputDefinition
input_label_max_length = 10

#QATestAttributeDefinition
max_length_qatestattributedefinition_label=100 #probably needs to be bigger

ATTR_TYPE_CHOICES = [('', '-------'), ('Bool Value', 'Bool Value'), \
('Float Value', 'Float Value'), ('Float Average Value',\
 'Float Average Value'), ('Hidden Bool Value', 'Hidden Bool Value') ]

#QATestResult
comment_max_length = 255

#FloatAverageValue
entered_values_max_length = 100

class Machine(models.Model):
	"""
	Machine includes treatment machines ie linear accelerators, CT scanners
	alternative name: TreatmentMachine
	
	is_visible denotes whether a machine should be available to be selected
	in data entry forms
	"""
	machine_name = models.CharField(max_length=machine_name_max_length)
	machine_type = models.CharField(max_length=machine_type_max_length)
	model = models.CharField(max_length=machine_model_max_length)
	serial_number = models.CharField(max_length=\
		machine_serial_number_max_length)
	installation_date = models.DateField()
	is_visible = models.BooleanField()
	def __str__(self):
		return self.machine_name

class Electrometer(models.Model):
	""" Table to contain data for all electrometers """
	electrometer_name = models.CharField(max_length =\
	 		electrometer_name_max_length)
	serial_number = models.CharField(max_length=\
		machine_serial_number_max_length)	
	manufacturer = models.CharField(max_length=\
			electrometer_manufacturer_max_length)
	model = models.CharField(max_length=electrometer_model_max_length)
	is_visible = models.BooleanField()
	def __str__(self):
		return self.electrometer_name

class IonChamber(models.Model):
	""" Table to contain data for all Ion Chambers """
	ion_chamber_name = models.CharField(max_length=ion_chamber_name_max_length)
	serial_number = models.CharField(max_length=\
			ion_chamber_serial_number_max_length)
	manufacturer = models.CharField(max_length=\
			ion_chamber_manufacturer_max_length)
	model = models.CharField(max_length=ion_chamber_model_max_length)
	calibration_date = models.DateField()
	calibration_factor = models.FloatField() 	#NOT SURE IF THIS SHOULD BE A 
												#FLOAT FIELD
	calibration_lab = models.CharField(max_length=\
			ion_chamber_calibration_lab_max_length)
	ion_chamber_type = models.CharField(max_length=ion_chamber_type_max_length)
	#ion_chamber_type should be enum Photon Electron Checkmate
	is_visible = models.BooleanField()
	def __str__(self):
		return self.ion_chamber_name
	
class QATestDefinition(models.Model):
	"""
	Table to contain basic definition data for a QA test.  variable_input
	is true only for tests that perform the same measurements over different
	LINAC beam strengths
	"""
	test_name = models.CharField(max_length = qa_test_name_max_length)
	frequency = models.CharField(max_length = qa_test_frequency_max_length)
	test_equip_required = models.BooleanField()
	temp_pressure_required = models.BooleanField()
	variable_input = models.BooleanField()
	is_visible = models.BooleanField()
	def __str__(self):
		return self.test_name

class QATestAttributeDefinition(models.Model):
	"""
	Each value that needs to be measured for a QA test is defined in this
	table
	"""
	qa_test_def_id = models.ForeignKey(QATestDefinition)
	label = models.CharField(max_length=\
			max_length_qatestattributedefinition_label)
	attribute_type = models.CharField(max_length=30, \
			choices = ATTR_TYPE_CHOICES)  #something about this definition 
			#doesn't really work,
			#values can be assigned outside of ATTR_TYPE_CHOICES, needs review
	form_order = models.SmallIntegerField()
	varied_input = models.BooleanField() 
	def __str__(self):
		return self.label

#this is a very troubling fit.  It forces a sort of over-association between 
#QATD and QATAR
#it clearly needs to exist but perhaps decoupled from QATD somehow
#Moreover, the input label as a string neglects the fact that it is associated
#with the LINAC beams "6MV", "18MV" and so on.  Need to revisit...
class QATestInputDefinition(models.Model):
	""" 
	Contains LINAC beam strength values for a QA Test Definitions whose
	variable_input paramaters are set to True
	"""
	input_label = models.CharField(max_length=input_label_max_length)
	qa_test_def_id = models.ForeignKey(QATestDefinition)
	form_order = models.SmallIntegerField()

class QATestResult(models.Model):
	"""
	The basic table for a QA Test Result.  Anything else that needs to be 
	entered for a test is kept in tables inherited from QA Test Attribute
	Result, Temperature Pressure table or Test Equipment table
	"""
	qa_test_def_id = models.ForeignKey(QATestDefinition)
	pub_date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)
	machine_id = models.ForeignKey(Machine)
	comment = models.CharField(max_length=comment_max_length, blank=True)
#	test_pass = models.BooleanField() #only true if all subtests pass, 
#   false if anything is not within spec, can't be implemented until I can
#	fill it in for the defined tests

	def __str__(self):
		optional0 = ""
		if self.pub_date.minute < 10:
			optional0 = "0"
		return str(self.qa_test_def_id) +" "+ str(self.machine_id) + \
	" %d/%d/%d" % (self.pub_date.day, self.pub_date.month, self.pub_date.year)

class TestEquipment(models.Model):
	""" Table containing test equipment selections for a QA test """
	qa_test_result_id = models.ForeignKey(QATestResult)
	electrometer = models.ForeignKey(Electrometer)
	ion_chamber = models.ForeignKey(IonChamber) #renamed from ionchamber
	#formerly had null=True for electrometer and ionchamber, now they
	#are mandatory

class TemperaturePressure(models.Model):
	""" Temperature and Pressure data for a QA test instance """
	qa_test_result_id = models.ForeignKey(QATestResult)
	temperature = models.FloatField()
	pressure = models.FloatField()	

class QATestAttributeResult(models.Model):
	"""
	Base class for Float Value, Bool Value and Float Average Value.
	Table contains all entered data for QA test forms that is specific
	to QA Test Attribute Definitions
	"""
	qa_test_result_id = models.ForeignKey(QATestResult)
	qa_test_attr_def_id = models.ForeignKey(QATestAttributeDefinition)
	qa_test_input_def_id = models.ForeignKey(QATestInputDefinition, \
				null = True)  #This is not be relevant to some tests

class BoolValue(QATestAttributeResult):
	""" Contains data for entered or calculated boolean values """
	value = models.BooleanField(default=False)
	
class FloatValue(QATestAttributeResult):
	""" Contains data for entered or calculated float values """
	value = models.FloatField()

class FloatAverageValue(QATestAttributeResult):
	""" 
	Contains entered data for form fields in which a mean is calculated
	from a number of entries 
	"""
	entered_values = models.CharField(max_length=entered_values_max_length)
	mean_value = models.FloatField()

#not complete, needs exclude_input and exclude_attribute, 
#not sure how, many to many??
class MachineTest(models.Model):
	"""
	Associative table to define which tests can be performed on which machines
	"""
	machine_id = models.ForeignKey(Machine)
	qa_test_def_id = models.ForeignKey(QATestDefinition)

class IonChamberAdditionalInfo(models.Model):
	"""
	Contains Ion-Chamber specific data for expected readings, upper and lower
	bounds for readings etc.
	"""
	ion_chamber_id = models.ForeignKey(IonChamber)
	machine_id = models.ForeignKey(Machine)
	input_label = models.CharField(max_length=input_label_max_length)
	expected_reading = models.FloatField(null=True)
	build_up_thickness = models.FloatField(null=True)
	energy_over_output_ratio_lower_bound = models.FloatField(null=True)
	energy_over_output_ratio_upper_bound = models.FloatField(null=True)
	expected_reading_PTW100SSD = models.FloatField(null=True)
	daily_photon_lower_bound= models.FloatField(null=True)
	daily_photon_upper_bound= models.FloatField(null=True)

