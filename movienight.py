#!/bin/env python

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from datetime import date
import pprint


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


imdb_url_showtimes = 'https://www.imdb.com/showtimes/'
default_location = 'CA/L7P3W6'
imdb_url_comingsoon = 'https://www.imdb.com/movies-coming-soon/'
this_month = get_this_month()
NUM_MONTHS = 8 # number of months to search ahead
all_movies = {}

class Movie:
    def __init__(self, release_date, title):
        self.release_date = release_date
        self.title = title
        self.genre = []
        self.outline = ""
        self.director = ""
        self.stars = []
        self.runtime = ""
        self.rating = ""

    def print(self):
        return "{0} : {1}".format(self.release_date, self.title)

    def __str__(self):
        return self.print()
    def __unicode__(self):
        return self.print()
    def __repr__(self):
        return self.print()

for i in range(0,NUM_MONTHS):
    next_month = get_x_month(this_month,i)
    all_movies[date_format(next_month)] = []
    raw_html = simple_get(imdb_url_comingsoon+date_format(next_month))
    full_page = BeautifulSoup(raw_html, 'html.parser')

    releases = []
    
    # <body> -> <div id=wrapper -> <div id=root -> <div id=pagecontent -> <div id=content-2-wide -> <div id=main -> <div class='article listo nm' -> <div class='list detail' -> <div class='list detail' 
    list_html = full_page.find("div", class_="list detail")
    #      -> <h4 -> <a href=[more info link>[title (year)]
    #      -> <p class='cert-runtime-genre 
    #        -> <img title='[cert]'
    #        -> <time >[runtime]
    #        -> <span >[genre] *repeats
    #      -> </p>
    #      -> <div class='outline'>[outline]
    #      -> <div class='txt-block -> <h5 class='inline'>Director: -> <span -> <a >[director]
    #      -> <div class='txt-block -> <h5 class='inline'>Stars: -> (<a >[actor])*
    release_date = ""
    data = list_html.children
    for child in data:
        #   -> <h4 class='li_group' -> <a name='[release date, ex Aug 30]'
        if child.name and 'h4' in child.name:
            release_date = child.text.strip()
        #   -> <div class='list_item odd' -> <table -> <tbody -> <tr -> <td class='overview-top 
        elif child.name and 'div' in child.name:
            # h4.text = "movie title (year)"
            movie = Movie(release_date, child.h4.text)
            # p.img.title = cert (if exists)
            # p.time.text = runtime
            # loop
            #   p.span.text = genre
            # div.class = 'outline' == outline
            # loop
            #   div.class = 'txt-block' 
            #     if h5.span.text == Director:
            #        a.text = director
            #     else h5.span.text == Stars:
            #        loop
            #          a.text = actor
            releases.append(movie)
        else:
            continue

    all_movies[date_format(next_month)].append(releases)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(all_movies)
