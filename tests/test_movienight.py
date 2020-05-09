import pytest
# test url
# connect to imdb_url and get 200
from requests import get
from movienight import MovieNightDefs as mnd
def test_url():
    r = get(mnd.imdb_url)
    assert r.status_code == 200, "Should be 200"

# test scrape page
# connect to imdb_url_coming_soon and get 200
def test_scrape_url():
    r = get(mnd.imdb_url_coming_soon)
    assert r.status_code == 200, "Should be 200"

# test scrape results
# results length > 0
# results contains filled out movie details
from movienight import MovieNight as mn
@pytest.fixture(scope="module")
def scrape_movies():
    mn = MovieNight()
    movies = mn.getMovies()
    return movies

def test_months(scrape_movies):
    assert len(scrape_movies) is mnd.NUM_MONTHS, "Should be {}".format(mnd.NUM_MONTHS)

def test_release_dates(scrape_movies):
    total = [ len(scrape_movies[x]) for x in scrape_movies.keys() ]
    #month = list(scrape_movies.keys())[0]
    #assert len(scrape_movies[month][0]) > 1, "Should be more than one movie being released in a single month"
    assert sum(total) > 1, "Should have found more than one movie"

def test_movie_details(scrape_movies):
    month = list(scrape_movies.keys())[2]
    assert len(scrape_movies[month][0][1].outline) > 1, "Movies should have an outline"
