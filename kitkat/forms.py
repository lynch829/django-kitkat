"""
forms.py
--------

Classes in this module define all data entry forms and components of forms
"""
#Catherine Bromhead, cathjb@gmail.com, November 20th, 2015

from django import forms
from django.contrib.auth.models import User
from .models import Machine, \
	QATestDefinition, Electrometer, IonChamber, QATestResult, \
	QATestAttributeResult, FloatValue, FloatAverageValue, TestEquipment, \
	TemperaturePressure, QATestAttributeDefinition, \
	QATestInputDefinition, BoolValue
from django.forms.extras.widgets import SelectDateWidget

#Operator choices for search filter form
OPERATOR_CHOICES = [('', '---'), ('GREATER THAN', '<='), ('LESS THAN', '>=')]

class SearchForm(forms.Form):
	"""
	form to enter search filters on the 'search.html' page
	"""
	qa_test_def_id = forms.ModelChoiceField(queryset = \
		QATestDefinition.objects.all(), label = "Test type", required = True)
	machine_id = forms.ModelChoiceField(queryset = \
		Machine.objects.all(), label = "Machine", required = False)
	user_id = forms.ModelChoiceField(queryset = \
		User.objects.all(), label = "User", required = False)
	date_from = forms.DateTimeField(widget = SelectDateWidget(), \
		label = "From date", required = False)
	date_to = forms.DateTimeField(widget = SelectDateWidget(), \
		label = "To date", required =  False)

class FloatSearchFilterForm(forms.Form):
	"""
	form to specify filtering parameters on a QA Test Attribute Result object
	of type Float Value
	"""
	label = forms.ChoiceField(choices = [("---","---")])
	operator = forms.ChoiceField(choices=OPERATOR_CHOICES)
	value = forms.FloatField()

	def set_label_choices(self, choices):
		self.fields['label'].choices = choices

class SelectMachineAndTestForm(forms.Form):
	"""
	Form displayed on home page in which a user can select a machine and a 
	test and progress to a data entry form for the selected test
	"""
	qa_test_def_id = forms.ModelChoiceField(queryset = \
		QATestDefinition.objects.filter(is_visible=True), label = \
		"Test type", required=True)
	machine_id = forms.ModelChoiceField(queryset = \
		Machine.objects.filter(is_visible=True), label = \
		"Machine", required=True)

class QATestResultForm(forms.ModelForm):
	"""
	Entry form for QA Test Result model
	"""
	qa_test_def_id=forms.ModelChoiceField\
		(queryset=QATestDefinition.objects.filter(is_visible=True), \
		label = "QA Test Type")
	machine_id = forms.ModelChoiceField(queryset=\
		Machine.objects.filter(is_visible=True))
	comment = forms.CharField(widget=\
		forms.Textarea(attrs={'cols': 25, 'rows': 3}), required = False)

	class Meta:
		model = QATestResult
		fields = ('qa_test_def_id', 'machine_id', 'comment')

class QATestAttributeResultForm(forms.ModelForm):
	"""
	Entry form for the QA Test Attribute Result table.  
	"""
	qa_test_attr_def_id = forms.ModelChoiceField(queryset = \
		QATestAttributeDefinition.objects.all(), widget = forms.HiddenInput())
	qa_test_input_def_id = forms.ModelChoiceField(queryset = \
		QATestInputDefinition.objects.all(), widget = forms.HiddenInput())
	qa_test_result_id = None # also automatic
	class Meta:
		model = QATestAttributeResult
		fields = ('qa_test_attr_def_id',)

class FloatValueForm(QATestAttributeResultForm):
	""" Entry form for Float Value """
	value = forms.FloatField()
	class Meta:
		model = FloatValue
		fields = ('value',)

	def set_label(self, vlabel):
		self.fields['value'].label = vlabel

class FloatAverageValueForm(QATestAttributeResultForm):
	""" Entry form for Float Average Value """
	entered_values = forms.CharField(widget=\
		forms.Textarea(attrs={'cols': 10, 'rows': 4}))
	mean_value = forms.FloatField(label="Mean")

	def set_label(self, vlabel):
		self.fields['entered_values'].label = vlabel
		#self.fields['mean_value'].label = mlabel

	class Meta:
		model = FloatAverageValue
		fields = ('entered_values', 'mean_value')

class BoolValueForm(QATestAttributeResultForm):
	""" Entry form for Bool Value """
	value = forms.BooleanField(required=True)
	class Meta:
		model = BoolValue
		fields = ('value',)

	def __init__(self, *args, **kwargs):
		QATestAttributeResultForm.__init__(self, *args, **kwargs)
		self.fields["value"].required = True

	def set_label(self, vlabel):
		self.fields['value'].label = vlabel

	def make_hidden(self):
		self.fields['value'].widget = forms.HiddenInput()

class TestEquipmentForm(forms.ModelForm):
	""" Entry form for Test Equipment """
	qa_test_result_id = None # also automatic
	electrometer = forms.ModelChoiceField\
		(queryset=Electrometer.objects.filter(is_visible=True), \
		required = True)
	ion_chamber = forms.ModelChoiceField(label="Ion Chamber", \
		queryset=IonChamber.objects.filter(is_visible=True), required = True)
	
	class Meta:
		model = TestEquipment
		fields = ('electrometer', 'ion_chamber')

	def limit_ion_chamber_options(self, ic_type):
		self.fields['ion_chamber'].queryset =IonChamber.objects.filter\
			(is_visible=True, ion_chamber_type=ic_type)

class TemperaturePressureForm(forms.ModelForm):
	""" Entry form for Temperature Pressure """
	qa_test_result_id = None # also automatic
	temperature = forms.FloatField()
	pressure = forms.FloatField()
	
	class Meta:
		model = TemperaturePressure
		fields = ('temperature', 'pressure')
