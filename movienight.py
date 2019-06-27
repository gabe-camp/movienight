#!/bin/env python

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from datetime import date
import pprint

#
# convenience functions for working with dates in url
#
def get_this_month():
    return date.today()


def get_next_month(d):
    return get_x_month(d, 1)


def get_x_month(d, x):
    year = d.year
    month = d.month
    month = month + x
    if month > 12:
        year = year + 1
        month = month - 12
    return date(year, month, 1)


# sample date = '/2019-02/'
def date_format(d):
    return d.strftime("/%Y-%m/")


#
# functions for grabbing url to scrape
#
# https://realpython.com/python-web-scraping-practical-introduction/ #
# start #
def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url,str(e)))


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') >= -1)


def log_error(e):
    print(e)
# end #


#
# static definitions
#
imdb_url = 'https://www.imdb.com/calendar'
default_region = '?region=CA'
NUM_MONTHS = 8
all_movies = {}


#
# data class
#
class Movie:
    '''
    Data class to hold movie details when scraping
    '''
    def __init__(self, release_date, title):
        self.release_date = release_date
        self.title = title
        self.genre = ""
        self.outline = ""
        self.director = ""
        self.stars = []
        self.runtime = ""
        self.rating = ""

    def print(self):
        return "{0} : {1} : {2} : {3}".format(
                    self.release_date,
                    self.title,
                    self.rating,
                    self.runtime)

    def __str__(self):
        return self.print()
    def __unicode__(self):
        return self.print()
    def __repr__(self):
        return self.print()

#
# do the scraping
#
raw_html = simple_get(imdb_url+default_region)
full_page = BeautifulSoup(raw_html, 'html.parser')
# type(full_page) = <class 'bs4.BeautifulSoup'>
releases = []
list_html = full_page.find("div", id="main")
for element in list_html.descendants:
   if 'Tag' in str(type(element)):
        if element.name == 'h4':
            # this is a date, ie '27 June 2019'
            # parse into a new date object
            # will be key for next releases seen for the all_movies dict
            # can use a timedelta to determine if we have hit NUM_MONTHS
            pass
        elif element.name == 'a':
            # this is the link to the page with the movie vitals (element['href'])
            # this is the title of the movie + year (element.string)
            pass


#pp = pprint.PrettyPrinter(indent=2)
#pp.pprint(all_movies)