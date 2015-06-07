import requests
import os
from sys import argv
import xml.etree.ElementTree as ET
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from server import app
from model import Book, Author, Location, Category, Quote, Event, Character, Award, connect_to_db, db
import pprint
import xml.etree.ElementTree as ET


apikey = os.environ['LIBRARYTHING_DEVELOP_KEY']

def get_local_venues(latitude, longitude):

	
	print "latitude, ", latitude
	
	print "longitude, ", longitude
	arguments = {"method" : "librarything.local.getvenuesnear", "lat" : latitude, 
	"lon": longitude, "distance":5, "venueType":1, "apikey" : apikey}
	local_venues = requests.get('http://librarything.com/services/rest/1.1/', params=arguments).text
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(local_venues)
	return local_venues    

def parse_local_venues(local_venues):
	# root = ET.fromstring(local_venues)
 #    ns={'lt':'http://www.librarything.com/'}
    pass

if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    script = argv

    get_local_venues()

