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

def return_local_venues(latitude, longitude):
	"""Gets longitudes and latitudes of user from the server/Google Geolocation API, runs through the 
	LibraryThing API which returns XML of local bookstore venues, parses through information to return 
	venue info (bookstore name, website, longitude, latitude), to server and picked up by ajax get in order
	to display locations with markers on a customized Google Map. """
	local_venues = get_local_venues(latitude, longitude)
	local_venues_list = parse_local_venues(local_venues)
	return local_venues_list

def get_local_venues(latitude, longitude):
	"""Runs the longitude and latitude through the LibraryThing API and returns bookstores within
	3 miles of the user."""

	arguments = {"method" : "librarything.local.getvenuesnear", "lat" : latitude, 
	"lon": longitude, "distance":3, "venueType":1, "apikey" : apikey}
	local_venues = requests.get('http://librarything.com/services/rest/1.1/', params=arguments).text
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(local_venues)
	return local_venues    

def parse_local_venues(local_venues):
	"""LibraryThing returns venue information as an XML.  This function uses lxml to parse through the XML
	and pull out listed information to place in a dictionary.  Function returns a list of dictionaries."""
	local_venues_list = []
	root = ET.fromstring(local_venues)
	ns={'lt':'http://www.librarything.com/'}
	places = root.findall('./lt:ltml/lt:itemList/lt:item', ns)
	for item in places:
		name = item.find('lt:name', ns).text
		website = item.find('lt:officialSite',ns).text
		latitude = item.find('lt:location/lt:lat',ns).text
		longitude = item.find('lt:location/lt:lng',ns).text
		local_venues_dict[name] = {website: website,
								latitude: latitude,
								longitude: longitude
								}
		local_venues_list.append(local_venues_dict)
		print "place, ", name
	return local_venues_list




if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    script = argv

    return_local_venues(latitude, longitude)