#!/bin/env python

from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from datetime import date
import json


PRINT_NICE = 1
PRINT_RAW = 2
PRINT_JSON = 3


#
# static definitions
#
class MovieNightDefs:
    imdb_url = 'https://www.imdb.com/'
    imdb_url_coming_soon = imdb_url + 'movies-coming-soon'
    default_region = '?region=CA'
    NUM_MONTHS = 8


#
# convenience functions for working with dates in url
#
class MovieNightUtils:
    @staticmethod
    def get_this_month():
        return date.today()

    @staticmethod
    def get_next_month(d):
        return MovieNightUtils.get_x_month(d, 1)

    @staticmethod
    def get_x_month(d, x):
        year = d.year
        month = d.month
        month = month + x
        if month > 12:
            year = year + 1
            month = month - 12
        return date(year, month, 1)

    @staticmethod
    def date_format(d):  # sample date = '/2019-02/'
        return d.strftime("/%Y-%m/")

    #
    # functions for grabbing url to scrape
    #
    # https://realpython.com/python-web-scraping-practical-introduction/ #
    # start #
    @staticmethod
    def simple_get(url):
        try:
            with closing(get(url, stream=True)) as resp:
                if MovieNightUtils.is_good_response(resp):
                    return resp.content
                else:
                    return None
        except RequestException as e:
            MovieNightUtils.log_error('Error during requests to {0} : {1}'.format(url, str(e)))

    @staticmethod
    def is_good_response(resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') >= -1)

    @staticmethod
    def log_error(e):
        print(e)
    # end #


#
# data class
#
class MovieNightData:
    """
    Data class to hold movie details when scraping
    """
    def __init__(self, release_date, title, mode=PRINT_JSON):
        self.release_date = release_date
        self.title = title
        self.genres = []
        self.outline = ""
        self.directors = []
        self.stars = []
        self.runtime = ""
        self.rating = ""
        self.mode = mode

    def print(self):
        if self.mode == PRINT_NICE:
            return self.print_nice()
        elif self.mode == PRINT_RAW:
            return self.print_raw()
        elif self.mode == PRINT_JSON:
            return self.print_json()
        else:
            return str(self)

    def print_nice(self):
        return "{0} : {1} : {2} : {3} : {4} : {5} : {6} : {7}".format(
                    self.release_date,
                    self.title,
                    self.rating,
                    self.runtime,
                    "".join(self.genres),
                    ",".join(self.directors),
                    ",".join(self.stars),
                    self.outline.strip())

    def print_raw(self):
        m = {"release_date": self.release_date,
             "title": self.title,
             "rating": self.rating,
             "runtime": self.runtime,
             "genres": self.genres,
             "directors": self.directors,
             "stars": self.stars,
             "outline": self.outline}
        return str(m)

    def print_json(self):
        m = json.dumps(self, separators=(',', ':'))
        return m

    def __str__(self):
        return self.print()

    def __unicode__(self):
        return self.print()

    def __repr__(self):
        return self.print()


class MovieNight:
    def __init__(self, args):
        pass

    def movienight(self):
        all_movies = {}
        this_month = MovieNightUtils.get_this_month()
        for i in range(0, MovieNightDefs.NUM_MONTHS):
            next_month = MovieNightUtils.get_x_month(this_month, i)
            all_movies[MovieNightUtils.date_format(next_month)] = []
            raw_html = MovieNightUtils.simple_get(
                MovieNightDefs.imdb_url_coming_soon + MovieNightUtils.date_format(next_month))
            full_page = BeautifulSoup(raw_html, 'html.parser')

            releases = []

            list_html = full_page.find("div", class_="list detail")
            am_parsing = False
            movie = ""
            release_date = ""  # many-to-one, release_date <-> title
            for child in list_html.descendants:
                if isinstance(child, Tag):
                    if 'h4' in child.name and len(child.attrs) > 0 and 'li_group' in child['class'][0]:  # release date
                        release_date = child.text.strip()
                    elif 'div' in child.name and len(child.attrs) > 0 and 'list_item' in child['class'][0]:  # title
                        # h4.text = "movie title (year)"
                        title = child.h4.text
                        if am_parsing:
                            # at this point we are finished parsing the current "list item"/movie
                            # so can add it to the months releases
                            releases.append(movie)
                            # and a new movie instance can be initiated
                            movie = MovieNightData(release_date, title)
                        else:
                            # first time through
                            movie = MovieNightData(release_date, title)
                            am_parsing = True
                        # p.img.title = cert (if exists)
                        # rating, runtime, genre
                        if child.p and len(child.attrs) > 0 and 'cert-runtime-genre' in child.p['class'][0]:
                            for tag in child.p.contents:
                                if isinstance(tag, Tag):
                                    if 'img' in tag.name:
                                        movie.rating = tag['title']
                        # p.time.text = runtime
                                    if 'time' in tag.name:
                                        movie.runtime = tag.text
                        #   p.span.text = genre
                                    if 'span' in tag.name:
                                        movie.genres.append(tag.text)
                    elif 'div' in child.name and 'outline' in child['class'][0]:  # outline
                        movie.outline = child.text
                    elif 'div' in child.name and 'txt-block' in child['class'][0]:  # director, stars
                        try:
                            if 'Director' in child.h5.text:
                                for tag in child.contents:
                                    if isinstance(tag, Tag):
                                        if 'a' in tag.name:
                                            movie.directors.append(tag.text.strip())
                        except AttributeError:
                            continue
                        try:
                            if 'Stars' in child.h5.text:
                                for tag in child.contents:
                                    if isinstance(tag, Tag):
                                        if 'a' in tag.name:
                                            movie.stars.append(tag.text.strip())
                        except AttributeError:
                            continue
                    else:
                        continue

            all_movies[MovieNightUtils.date_format(next_month)].append(releases)
        return all_movies


if __name__ == '__main__':
    #
    # opts
    # - num_months
    # - filters
    #   - actor list
    #   - genre list
    #   - director list
    # - print format (json, csv, raw?)
    #
    movies = MovieNight.movienight()

    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(movies)
