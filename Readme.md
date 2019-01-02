# Doordenkertjes (Dutch for "Brain Teasers")

Version 1.0.2
Code (c) 2014-2016 Digital Humanities Lab, Utrecht University
Illustrations (c) 2015 Birgit Gorter

This is an application meant to inspire daycare workers in ethical reflection. It is available both as a website and as a phone application (soon to be released). The homepage is at https://doordenkertjes.hum.uu.nl/. For more information, see https://doordenkertjes.hum.uu.nl/#about (Dutch).


## Technical information

This is a hybrid [Flask](http://flask.pocoo.org) web application/[PhoneGap](http://phonegap.com) cross-platform phone application. The client side consists of a single HTML file that can run either inside a browser or inside a web view within a native mobile phone application, without modification. The server side is a Flask application that responds to JSON requests and offers a web-based administration interface.

The Git repository uses the git-flow branching model.


### Project overview

The inner `daycare_ethics` directory (the one that contains `config.xml` and `__init__.py`) serves both as the top-level Python package and as the PhoneGap project directory. Inside it are several subdirectories, some of which belong to the Flask application and some of which belong to PhoneGap.

`admin`, `database` and `server` belong to the Flask part. They define the administration interface, database and public JSON interface, respectively. The administration interface is based on the Flask-Admin package. The database definition uses SQLAlchemy declarative models.

`test` also belongs to the Flask part and defines unit tests for the entire Python application. Its internal layout mimics that of the application.

`hooks` and `res` belong to the PhoneGap part. The former does not contain anything important. The latter contains multimedia that are specifically meant for the PhoneGap native application wrapper, i.e. icons and splash screens in multiple formats.

When you start using PhoneGap, this will also create `platforms` and `plugins` directories.

The `www` directory belongs to both; its name is dictated by the PhoneGap framework but it serves at the same time as what would usually be the `static` directory for a Flask application. It contains the regular client-side code: scripts, style sheets and images. All JavaScript libraries are stored locally, because a PhoneGap application must still work when there is no internet connection. Note that the `index.html` is not a template; the public client side does not use templates because that would be impractical for web view deployment.

`www/spec` contains a [Jasmine](https://jasmine.github.io)-based test suite for the JavaScript part.


### How to install and test locally

It is recommended that you create a Python 2.7 virtualenv with the pip-tools package installed. Activate the virtualenv and run `pip-sync` in order to install all dependencies. **Note:** at the time of writing, pip-tools does not support pip version 8 or later. Run `pip install -U pip==7.1.2` first to be sure that you have the latest compatible version of pip.

In order to run the server side test suite, simply run `python test.py`. This automatically runs all test suites in the `daycare_ethics/tests` directory. The test suite is entirely self-contained; you do not need anything other than the Python packages inside the virtualenv.

In order to run the client side test suite, open `daycare_ethics/www/spec/SpecRunner.html`. This only requires a local copy of the code. Once you have the server running locally as detailed below, you can also visit http://127.0.0.1:5000/spec/SpecRunner.html.

In order to run a local version of the server side, you need a persistent local database, a JSON data file to supply the CAPTCHA system and a configuration file from which the Python application can read its parameters.

Before first use you have to create an empty database, possibly with an associated user; consult the documentation of your RDBMS for instructions. The application is known to work with recent versions of MySQL and SQLite and it will probably work with other RDBMSs.

The CAPTCHA JSON file should define an object in which every key names a category and the corresponding value is an array of words that belong to that category. See `daycare_ethics/tests/data/test_captcha.json` for an example. You should not use that example, because it has been published publicly. More data makes the captcha safer; we recommend at least 10 categories with at least 30 words per category. A slight overlap between the categories is allowed. Words must not contain whitespace. It is wise to stick to the ASCII character set and to write all words in lowercase (unlike in the example).

The configuration file should at least contain the following fields:

    SQLALCHEMY_DATABASE_URI = 'mysql://user@localhost/dbname?charset=utf8&use_unicode=0'
    SECRET_KEY = '...' # long random string
    CAPTCHA_DATA = '/absolute/path/to/captcha/data.json'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

You may optionally set the `SESSION_COOKIE_NAME` if you want it to be something other than "session". Consult the SQLAlchemy documentation for details on the database URI. If you call the configuration file `config.py` it will be automatically ignored by Git.

Once you have the above requirements in place, run your local test server with the following command:

    python run.py path/to/config.py

The path should be either relative to the inner `daycare_ethics` directory or absolute.

Running the test server creates a new `instance` directory next to `daycare_ethics`. Media that you upload to the application will be saved there. Debugging output will go straight to your terminal.

You can open the client side interface either by opening `daycare_ethics/www/index.html` in your browser (this does not work in Google Chrome) or by visiting http://127.0.0.1:5000. The administration interface is at http://127.0.0.1:5000/admin. However, at this point the `index.html` is still "phoning home" to doordenkertjes.hum.uu.nl. In order to see your own content in the public interface, patch the bottom of `index.html` as follows:

    -    app.origin = 'https://doordenkertjes.hum.uu.nl/';
    +    app.origin = 'http://127.0.0.1:5000/';


### How to deploy to a server

As above, you need a virtualenv with the required Python packages, a database, a JSON CAPTCHA file and a configuration file. Patch the `app.origin` in your `index.html` with the server address. Deployment is otherwise completely regular for a Flask application; consult the Flask documentation for instructions. Your WSGI interface file should import and call the application factory roughly as follows:

    from daycare_ethics import create_app

    application = create_app(config_file=path_to_config_py,
                              instance=custom_instance_folder_path )

    # optionally add handlers to application.logger here

The instructions for logging can also be found in the Flask documentation.

By default, the administration interface is **unprotected**. You have to take your own measures to prevent unauthorized tinkering. We recommend that you use SSL and arrange LDAP or a similar authentication method at the server level to protect `/admin`.

The illustrations are **copyrighted** and you cannot reuse them without explicit permission by Birgit Gorter. Please contact us for permission or use your own illustrations instead.


### How to deploy the PhoneGap application

Install PhoneGap or Cordova through the Node Package Manager (npm). See the official documentation for instructions. Since this is a cross-platform application, you have to follow the instructions for the command line interface (CLI). You have to set your working directory to the inner `daycare_ethics` whenever you issue commands to PhoneGap or Cordova, because it depends on the `config.xml` in there.

The application depends on the following plugins, which you can install with `phonegap plugin add`:

  * `cordova-open`
  * `cordova-plugin-inappbrowser`
  * `cordova-plugin-whitelist`

In order to build the application and run it in an emulator, use the following command:

    phonegap run <platform>

Note that only the platforms `ios` and `android` have been tested so far. You may add the `--device` option to install to a connected physical device instead. Consult the manual of your vendor IDE for further instructions on how to connect your device.

In order to just build without installing, replace `run` by `build`. For publication to an app store, use the `--release` flag.
