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
imdb_url_showtimes = 'https://www.imdb.com/showtimes/'
default_location = 'CA/L7P3W6'
imdb_url_comingsoon = 'https://www.imdb.com/movies-coming-soon/'
this_month = get_this_month()
NUM_MONTHS = 8 # number of months to search ahead
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
for i in range(0,NUM_MONTHS):
    next_month = get_x_month(this_month,i)
    all_movies[date_format(next_month)] = []
    raw_html = simple_get(imdb_url_comingsoon+date_format(next_month))
    full_page = BeautifulSoup(raw_html, 'html.parser')
    # type(full_page) = <class 'bs4.BeautifulSoup'>
    releases = []
    list_html = full_page.find("div", class_="list detail")
    # type(list_html) = <class 'bs4.element.Tag'>
    release_date = ""
    data = list_html.children
    # type(data) = <class 'list_iterator'>
    for child in data:
        # get date under which a list of movies will be released on
        if child.name and 'h4' in child.name:
            release_date = child.text.strip()
        # get movie title(s) corresponding to the already found release_date
        elif child.name and 'div' in child.name:
            movie = Movie(release_date, child.h4.text)
            #print("--|" + child.text + "|--")
            # get other data from child and set it in movie
            # genre
            if child.p.img:
                #print("Rating: {0}".format(child.p.img['title']))
                movie.rating = child.p.img['title']
            # outline

            # director

            # stars

            # runtime
            if child.p.time:
                movie.runtime = child.p.time.text
            # rating
            releases.append(movie)
        else:
            continue

    all_movies[date_format(next_month)].append(releases)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(all_movies)