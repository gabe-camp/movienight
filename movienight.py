#!/bin/env python

from bs4 import BeautifulSoup
from bs4.element import Tag
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
imdb_url = 'https://www.imdb.com/'
imdb_url_coming_soon = imdb_url + 'movies-coming-soon'
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
        self.genres = []
        self.outline = ""
        self.directors= []
        self.stars = []
        self.runtime = ""
        self.rating = ""

    def print(self):
        return "{0} : {1} : {2} : {3} : {4} : {5} : {6} : {7}".format(
                    self.release_date,
                    self.title,
                    self.rating,
                    self.runtime,
                    "".join(self.genres),
                    ",".join(self.directors),
                    ",".join(self.stars),
                    self.outline.strip())

    def __str__(self):
        return self.print()
    def __unicode__(self):
        return self.print()
    def __repr__(self):
        return self.print()


this_month = get_this_month()
for i in range(0,NUM_MONTHS):
    next_month = get_x_month(this_month,i)
    all_movies[date_format(next_month)] = []
    raw_html = simple_get(imdb_url_coming_soon+date_format(next_month))
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
    for child in list_html.descendants:
        if isinstance(child, Tag):
            #   -> <h4 class='li_group' -> <a name='[release date, ex Aug 30]'
            if 'h4' in child.name and len(child.attrs) > 0 and 'li_group' in child['class'][0]:
                release_date = child.text.strip()
            #   -> <div class='list_item odd' -> <table -> <tbody -> <tr -> <td class='overview-top
            elif 'div' in child.name and len(child.attrs) > 0 and 'list_item' in child['class'][0]:
                # h4.text = "movie title (year)"
                movie = Movie(release_date, child.h4.text)
                # p.img.title = cert (if exists)
                genres = []
                if child.p and len(child.attrs) > 0 and 'cert-runtime-genre' in child.p['class'][0]:
                    for tag in child.p.contents:
                        if isinstance(tag, Tag):
                            if 'img' in tag.name:
                                movie.rating = tag['title']
                # p.time.text = runtime
                            if 'time' in tag.name:
                                movie.runtime = tag.text
                # loop
                #   p.span.text = genre
                            if 'span' in tag.name:
                                movie.genres.append(tag.text)
                # div.class = 'outline' == outline
            elif 'div' in child.name and 'outline' in child['class'][0]:
                movie.outline = child.text
                # loop
                #   div.class = 'txt-block'
                #     if h5.span.text == Director:
                #        a.text = director
            elif 'div' in child.name and 'txt-block' in child['class'][0]:
                try:
                    if 'Director' in child.h5.text:
                        for tag in child.contents:
                            if isinstance(tag, Tag):
                                if 'a' in tag.name:
                                    movie.directors.append(tag.text.strip())
                except AttributeError as ae:
                    print("{0}".format(child))
                #     else h5.span.text == Stars:
                #        loop
                #          a.text = actor
                try:
                    if 'Stars' in child.h5.text:
                        for tag in child.contents:
                            if isinstance(tag, Tag):
                                if 'a' in tag.name:
                                    movie.stars.append(tag.text.strip())

                        # at this point we are finished parsing the current "list item"/movie
                        # so can add it to the months releases
                        releases.append(movie)
                except AttributeError as ae:
                    print("{0}".format(child))

            else:
                continue



    all_movies[date_format(next_month)].append(releases)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(all_movies)
