Instructions for running software in development mode
-----------------------------------------------------

These instructions are for running the app in development mode using
the dbsqlite3 database.

Requirements:

	- Python 2.7

	- Django 1.8

	- Pytz    (for timezone support)

If python 2.7 is installed the remaining two can be installed using

	pip install django

	pip install pytz

Once these are installed the web app can be seen using the command

	python manage.py runserver

within the django-kitkat directory.  Once the development server is running
the web page can be found at

http://127.0.0.1:8000/kitkat/home/

NOTE: The software can be deployed on a Windows 2008 server at the Alfred
Hospital using the CherryPy package as the application server and a MySQL
backend.  These develompent mode instructions are appropriate for somebody
who is examining the software as a Masters project.
