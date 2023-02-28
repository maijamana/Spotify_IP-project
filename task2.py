import base64
import requests
import json
client_id = 'faa359690849484eaf9ae8d6f1c3353d'
client_secret = 'aa445e96f01343afbb14337da971ab84'

artist_name = input('Введіть ім`я виконавця: ')
country_name = input('Введіть вашу країну у форматі ISO-2: ')

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

token = get_token(client_id, client_secret)

def get_auth_header(token):
    '''
    Returns headers for requests get
    '''
    return {'Authorization': 'Bearer '+token}

def get_markets(token):
    '''
    Returns all aviable markets
    '''
    url = f'https://api.spotify.com/v1/markets'
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['markets']
    return json_result
if country_name not in get_markets(token):
    print('Spotify недоступний у вашій країні')

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

result = search_for_artist(token, artist_name)
artist_id = result['id']

def get_song_by_artist(token, artist_id, country_name):
    '''
    Returns 10 top tracks songs by artist_id
    '''
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country={country_name}'
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

songs = get_song_by_artist(token, artist_id, country_name)

def song_printing(songs, country_name):
    '''
    This func printing top 10 songs in country_name
    '''
    print(f'Топ 10 найпопулярніших пісень в {country_name}:')
    for idx, song in enumerate(songs):
        print(f'{idx+1}. {song["name"]}')

def get_albums_by_artist(token, artist_id):
    '''
    Returns all albums by artist_id
    '''
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['items']
    return json_result

albums = get_albums_by_artist(token, artist_id)

def albums_printing(albums, id = False):
    '''
    Func returns dict of albums id if id = True. If not - printing all artist`s albums
    '''
    if not id:
        for idx, album in enumerate(albums):
            print(f'{idx+1}. {album["name"]}')
    else:
        albums_id = {}
        for idx, album in enumerate(albums):
            albums_id[idx+1] = album["id"]
        return albums_id

def get_related_artists_by_artist(token, artist_id):
    '''
    Returns related artists by artist_id
    '''
    url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['artists']
    return json_result

related_artists = get_related_artists_by_artist(token, artist_id)

def related_artists_printing(related_artists):
    '''
    This func printing related artists
    '''
    for idx, rel_artist in enumerate(related_artists):
        print(f'{idx+1}. {rel_artist["name"]}')

def get_songs_by_album(token, album_id):
    '''
    Returns songs by album_id
    '''
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['items']
    return json_result

def albums_songs_printing(albums_songs):
    '''
    This func printing album`s song
    '''
    for idx, song in enumerate(albums_songs):
        print(f'{idx+1}. {song["name"]}')

inp = ['something']
while len(str(inp))!=0:
    print(' ')
    print('Можливі опції:')
    print('1. Показати топ 10 треків виконавця\n2. Показати всі альбоми \
виконавця\n3. Показати всі пісні альбому\n4. Показати схожих виконавців')
    try:
        inp = int(input('Введіть номер опції: '))
    except TypeError:
        print('Введіть число!')
    if inp == 1:
        song_printing(songs, country_name)
    elif inp == 2:
        albums_printing(albums, id = False)
    elif inp == 3:
        albums_printing(albums, id = False)
        numb = int(input('Введіть номер альбому: '))
        album_id = albums_printing(albums, id = True)[numb]
        albums_songs = get_songs_by_album(token, album_id)
        albums_songs_printing(albums_songs)
    elif inp == 4:
        related_artists_printing(related_artists)
    else:
        print('Введіть число з запропонованих!')
