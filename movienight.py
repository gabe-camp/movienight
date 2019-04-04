#!/bin/env python

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from datetime import date
import pprint

NUM_MONTHS = 12 # number of months to search ahead


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

# div class="list detail"
#   h4 class=li_group <<< Month and day in which movies are released
#   div class="list_item odd" | "list_item even"
#       table class="nm-title-overview-widget-layout"
#           tbody
#               td id="img_primary"  << movie poster img
#               td class="overview-top"
#                   h4  << title (year)
#                   p class="cert-runtime-genre"
#                       img class="absmiddle certimage" title=<rating>
#                       time << running time
#                       span <genre>
#                       span <genre>
#                   div class="rating_txt"
#                       span <metascore>
#                   div class="outline"
#                       div class="txt-block"
#                           h5 class="inline" Director
#                           a href <name>
#                       div class="txt-block
#                           h5 class="inline" Stars
#                           a href <name>
#                           a href <name>

imdb_url_showtimes = 'https://www.imdb.com/showtimes/'
default_location = 'CA/L7P3W6'
imdb_url_comingsoon = 'https://www.imdb.com/movies-coming-soon/'
this_month = get_this_month()
all_movies = {}
#month = {}
for i in range(0,NUM_MONTHS):
    next_month = get_x_month(this_month,i)
    #month[date_format(next_month)] = []
    all_movies[date_format(next_month)] = []
    raw_html = simple_get(imdb_url_comingsoon+date_format(next_month))
    html = BeautifulSoup(raw_html, 'html.parser')

    releases = {}
    content = html.find("div", class_="list detail")
    for release_day in content.find_all("h4", class_="li_group"):
        release_day_text = release_day.text.strip()
        releases[release_day_text] = []
        #print(release_day_text)

    all_movies[date_format(next_month)].append(releases)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(all_movies)