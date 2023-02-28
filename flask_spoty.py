from flask import Flask, render_template, request
import base64
import requests
import json
import pycountry
import folium
from geopy.geocoders import Nominatim

client_id = 'faa359690849484eaf9ae8d6f1c3353d'
client_secret = 'aa445e96f01343afbb14337da971ab84'

def get_token(client_id, client_secret):
    '''
    This function returns token from request
    '''
    client_creds = f'{client_id}:{client_secret}'
    client_creds_b64 = str(base64.b64encode(client_creds.encode('utf-8')), 'utf-8')
    token_url = 'https://accounts.spotify.com/api/token'
    token_headers = {
        'Authorization': 'Basic ' + client_creds_b64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_data ={
        'grant_type':'client_credentials'
    }
    r = requests.post(token_url, data = token_data, headers = token_headers)
    token = r.json()['access_token']
    return token

def get_auth_header(token):
    '''
    Returns headers for requests get
    '''
    return {'Authorization': 'Bearer '+token}

def search_for_artist(token, artist_name):
    '''
    Returns information about artist: external_urls, followers, genres,
    href, id, images, name, popularity, type, uri.
    '''
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={artist_name}&type=artist&limit=1'
    query_url = url + query
    result = requests.get(query_url, headers = headers)
    json_result = json.loads(result.content)['artists']['items']
    if len(json_result) == 0:
        print('Sorry, we cannot find an artist with this name')
        return None
    return json_result[0]

def get_song_by_artist(token, artist_id):
    '''
    Returns 10 top tracks songs by artist_id
    '''
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=UA'
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

def get_available_markets_by_song(token, best_song_id):
    '''
    Returns 10 top tracks songs by artist_id
    '''
    url = f"https://api.spotify.com/v1/tracks/{best_song_id}"
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['available_markets']
    return json_result


def map_returns(artist_name):
    token = get_token(client_id, client_secret)
    result = search_for_artist(token, artist_name)
    artist_id = result['id']
    songs = get_song_by_artist(token, artist_id)
    best_song_id = songs[0]['id']
    markets = get_available_markets_by_song(token, best_song_id)

    country_list = []
    for country in markets:
        country_list.append(pycountry.countries.get(alpha_2=country))
    countries = []
    for i in country_list:
        try:
            countries.append(i.name.split(',')[0])
        except AttributeError:
            continue
    map_s = folium.Map()
    geolocator = Nominatim(user_agent="spoty_map")
    for i in countries[:2]:
        location = geolocator.geocode('Argentina')
        latitude = location.latitude
        longitude = location.longitude
        map_s.add_child(folium.Marker(location=[latitude, longitude],popup = i, icon=folium.Icon()))
    map_s.save('map_spoty.html')
    return map_s

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def return_map():
    artist = request.form['typing...']
    title = 'Look at your result!'
    result = map_returns(artist)
    return render_template('home.html', map = result._repr_html_(), )

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True)