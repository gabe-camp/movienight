from flask import Flask, request
from movienight import MovieNight
from flask_cors import CORS
import config

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
@app.route('/movies', methods=['POST'])
def movies():
    req_data = request.get_json()
    try:
        months = 1
        if 'months' in req_data:
            months = req_data['months']
        actors = []
        if 'actors' in req_data:
            actors = req_data['actors']
        genres = []
        if 'genres' in req_data:
            genres = req_data['genres']
        directors = []
        if 'directors' in req_data:
            directors = req_data['directors']
    except TypeError:
        #print('{}\n{}\n{}'.format(request.headers,request.get_data(), request.get_json()))
        return None
    mn = MovieNight(months=months, actors=actors, genres=genres, directors=directors)
    r = mn.getMovies()
    if r > 0:
        print('{}'.format(mn.toJSON()))
        return mn.toJSON()
    else:
        return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, nargs='?', default='0.0.0.0')
    args = parser.parse_args()
    app.run(host=args.host, port=config.PORT, debug=config.DEBUG_MODE)
