#!/bin/env python

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from datetime import date


def get_this_month():
    return date_format(date.today())


def get_next_month(d):
    year = d.year
    month = d.month
    month = month + 1
    if month > 12:
        year = year + 1
        month = 1
    return date_format(date(year, month, 1))


def date_format(d):
    return d.strftime("/%Y-%m/")


imdb_url_showtimes = 'https://www.imdb.com/showtimes/'
default_location = 'CA/L7P3W6'
imdb_url_comingsoon = 'https://www.imdb.com/movies-coming-soon/'
# sample date = '/2019-02/'
this_month = get_this_month()

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

# body
#   div id=wrapper
#       div id=root
#           div id=pagecontent class=pagecontent
#               div id=content-2-wide class=redesign
#                   div id=main
#                       div class="article listo nm"
#                           div class="list detail"
#                               h4 class=li_group <<< Month and day in which movies are released
#                               div class="list_item odd" | "list_item even"
#                                    table class="nm-title-overview-widget-layout"
#                                       tbody
#                                           td id="img_primary"  << movie poster img
#                                           td class="overview-top"
#                                               h4  << title (year)
#                                               p class="cert-runtime-genre"
#                                                   img class="absmiddle certimage" title=<rating>
#                                                   time << running time
#                                                   span <genre>
#                                                   span <genre>
#                                               div class="rating_txt"
#                                                   span <metascore>
#                                               div class="outline"
#                                               div class="txt-block"
#                                                   h5 class="inline" Director
#                                                   a href <name>
#                                               div class="txt-block
#                                                   h5 class="inline" Stars
#                                                   a href <name>
#                                                   a href <name>
raw_html = simple_get(imdb_url_comingsoon+this_month)
html = BeautifulSoup(raw_html, 'html.parser')
#print(html.prettify())
for child in html.find("div", class_="list detail").children:
    print(child)