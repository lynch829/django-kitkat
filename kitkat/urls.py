from django.conf.urls import url
from django.contrib.auth.views import login, logout
from django.contrib.auth.decorators import login_required


from . import forms
from . import views

urlpatterns = [
	url(r'^home/+$', views.home, name = 'home'),
    url(r'^process_machine_and_test_form/+$', views.process_machine_and_test_form, name='process_machine_and_test_form'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^login_form/$', views.login_form, name='login_form'),
    url(r'^process_qa_form/$', views.process_qa_form, name='process_qa_form'),
	url(r'^(?P<test_result_id>[0-9]+)/display_entry/+$', views.display_entry, name = 'display_entry'),
	url(r'^(?P<qa_test_def>[0-9]+)/(?P<machine>[0-9]+)/past_results/+$', views.past_results, name = 'past_results'),
    url(r'^user_logout/$', views.user_login, name='user_logout'),
    url(r'^recent_results_daily_photon_output_test/$', views.recent_results_daily_photon_output_test, name='recent_results_daily_photon_output_test'),
    url(r'^search/$', views.search, name='search'),
    url(r'^searchdb/$', views.searchdb, name='searchdb'),
    url(r'^list_machines_for_test/$', views.list_machines_for_test, name='list_machines_for_test'),
	url(r'^additional_filters/$', views.additional_filters, name='additional_filters'),
	url(r'^list_filters_for_test/$', views.list_filters_for_test, name='list_filters_for_test'),
    url(r'^get_dpot_bounds/$', views.get_dpot_bounds, name='get_dpot_bounds'),
    url(r'^get_ion_chamber_expected_readings/$', views.get_ion_chamber_expected_readings, name='get_ion_chamber_expected_readings'),
    url(r'^get_ratio_bounds/$', views.get_ratio_bounds, name='get_ratio_bounds'),

]
