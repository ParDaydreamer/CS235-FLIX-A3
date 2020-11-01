# CS235 Flix

## Introdution
This is the COMPSCI 235 Assignment 3 project by Gary Zou.

Feel free to enjoy some movies in this movie application, and don't forget to leave some reviews!

## Features
* Browse movies by genres on left navigation bar
* Browse movies by actors on right sidebar
* Browse movies by directors on right sidebar and with clickable link (in orange) in all movie listings
* Browse movies by years with clickable link (in red) in all movie listings
* Register for an account
* Login with registered account
* View reviews on all movies (Login required)
* Add reviews to all movies with a rating between 1 and 10 (Login required)
* Browse for movie posters (Internet connection required)


## Description

A Web application that demonstrates use of Python's Flask framework. The application makes use of libraries such as the Jinja templating library and WTForms. Architectural design patterns and principles including Repository, Dependency Inversion and Single Responsibility have been used to design the application. The application uses Flask Blueprints to maintain a separation of concerns between application functions. Testing includes unit and end-to-end testing using the pytest tool. 
This application used SQLAlchemy for a SQL database.
## Installation

**Installation via requirements.txt**

```shell
$ cd CS235-FLIX-A3
$ py -3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

When using PyCharm, set the virtual environment using 'File'->'Settings' and select 'Project:CS235-FLIX-A3' from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add'. Click the 'Existing environment' radio button to select the virtual environment. 

## Execution

**Running the application**

From the *CS235-FLIX-A3* directory, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
$ flask run
```` 


## Configuration

The *CS235-FLIX-A3/.env* file contains variable settings. They are set with appropriate values.

* `FLASK_APP`: Entry point of the application (should always be `wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForm library.


## Testing

Testing requires that file *CS235-FLIX-A3/tests/conftest.py* be edited to set the value of `path`. You should set this to the absolute path of the project's destination, i.e. the directory to *STORE* this project.

(e.g. If you are storing this project on your desktop, then the `path` should be your desktop.)

*DO NOT* set `path` to the `CS235-FLIX-A3` directory.

E.g. 

* `path = os.path.join('/Users/garym8/PycharmProjects/DEP')` (Macintosh)
* `path = os.path.join('C:', os.sep, 'Users', 'iwar006', 'Documents', 'Python dev')` (Windows PC)

You can then run tests from within PyCharm.

 