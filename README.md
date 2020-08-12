# Nottingtable
Nottingtable is a web system that allows UNNC students to 
get their teaching timetable in ical (.ics) format.

## Built with
### Main Python Library 
- [arrow](https://github.com/arrow-py/arrow)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
- [click](https://github.com/pallets/click)
- [Flask](https://github.com/pallets/flask/)
- [Flask-SQLAlchemy](https://github.com/pallets/flask-sqlalchemy)
- [iCalendar](https://github.com/collective/icalendar)
- [lxml](https://github.com/lxml/lxml)
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)
- [requests](https://github.com/psf/requests)
### Required Database
[MySQL 8.0](https://dev.mysql.com/downloads/) and Python MySQL client [PyMySQL](https://github.com/PyMySQL/PyMySQL).

## Features
For student users:
- Get your teaching timetable out of your box.
- Import your timetable to any kind of calendar client as you like.
- If this web system is deployed on Internet, you can also subscribe 
your timetable online to get updates.

For those who want to provide timetable related services to UNNC students:
- This system is fully open sourced and easy to deploy to your own server.
- You could make use of the API provided by this web system to get timetable
in JSON format, which is much easier to parse.
- Or you might want to use crawler module in this system directly to integrate with your service.

## Deploy Guide
*This deploy guide will not tell you how to setup a MySQL server, 
how to install python environment, and etc..*
1. Clone this repository:

    `git clone https://github.com/Steven1677/nottingtable-flask.git`
   
2. Create a virtual environment for this project (optional, but highly recommended):
    
    `cd nottingtable-flask`
    
    `python3 -m venv venv`

3. Activate the virtual environment
    
    `source ./venv/bin/activate`

4. Install the Python library dependencies:

    `(venv) pip install -r requirements.txt`

5. Export environment variables for this project:

    `(venv) export DATABASE_URI=pymysql://database_user:password@database_address:port/database_name`
    
    Please replace your database setups to the connection string.
    
    Note: The user should have the all the rights to that database.

6. Change configuration in `nottingtable/config.py`
    
    Please pay attention to `BASE_URL` `FIRST_MONDAY` `YEAR1_PDF_URL` `CACHE_LIFE`.
    
7. One more step to run the program:

    `(venv) export FLASK_APP=app.py`
    
    `flask init-all`
    
8. Use flask builtin server to test the configuration before:

    `flask run`

Now, the basic deployment finishes. For the production-ready
deployment, please refer to [Wiki](https://github.com/Steven1677/nottingtable-flask/wiki/Deploy-for-Production).

## Contribute
As an open sourced program, any contributes to this project is welcome.

*Especially for a modern frontend design*

## Credits
[CorsairCat](https://github.com/CorsairCat), who built the PHP version of this program,
and inspired me about the crawler's database model.

[Songkeys](https://github.com/Songkeys), main developer of uCourse, a popular
WeChat mini program among UNNC students, which aimed at showing timetable on WeChat.
He provided me a lot of details behind school's timetabling service implementation,
which make my development much easier.

## License
Apache License 2.0