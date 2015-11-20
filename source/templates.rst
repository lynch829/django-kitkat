templates
---------

home.html
~~~~~~~~~

Context: select_form, tbl

The application home page.  Data is sent to this page from views.home.  The
page contains a blank instance of forms.SelectMachineAndTestForm and a table
of most recently entered test data.  The page contains links to most recently
performed test summaries, the search page and the admin page

qa_testforms.html
~~~~~~~~~~~~~~~~~

Context: result_form, attribute_forms, prelim_forms, hidden_forms, input_labels,
scripts

This page displays a data entry form for a QA test assembled in 
views.process_qa_form.  The HTML document uses the Django template language
to display an arbitrary number of form components in a data entry table.
The template is passed the name of a javascript file to use.

linacmechanicalcheck.html
~~~~~~~~~~~~~~~~~~~~~~~~~

Context: result_form, formatted_groups, scripts, input_labels

Template written specifically to render the entry form for the Linac Mechanical 
Check, but could potentially be extended to other test types.  The form is 
rendered from the views.linac_mechanical_check_view method.

searchform.html
~~~~~~~~~~~~~~~

Context: search_form

Template to display the search page.  Contains a blank search form.  When form
is filled in, data is passed to the views.searchdb method.

login.html
~~~~~~~~~~

A template for a basic login page, upon submission redirects to 
views.user_login method

filters.html
~~~~~~~~~~~~

A snippet of code that is included in the searchform.html page dynamically
by the javascript file searchform.js


