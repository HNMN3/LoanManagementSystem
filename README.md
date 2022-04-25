# Requirements
This project is written in Python 3.8.
The required libraries to run the project are written in the requirements.txt file.

# Installation
Make sure that python 3.8 is installed on your system.
Create a virtual environment and install the required libraries using the command:
```
pip install -r requirements.txt
```

Create one admin user using the command:
```
python manage.py createsuperuser
```

Migrate the database using the command:
```
python manage.py migrate
```

Run the tests using the command:
```
python manage.py test
```

Run the local server using the command:
```
python manage.py runserver
```

You can now access the APIs on the local server.

To the the API documentation, go to the documentation page:
```
https://documenter.getpostman.com/view/1872196/UyrBibdY
```
