import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope='user-top-read'
)

def get_top_tracks():
    auth_url = sp_oauth.get_authorize_url()
    print(f'Please navigate here to authorize: {auth_url}')

    response = input('Enter the URL you were redirected to: ')
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_tracks(limit=20, time_range='long_term')
    
    for idx, item in enumerate(results['items']):
        print(f"{idx + 1}. {item['name']} by {item['artists'][0]['name']}")

def get_top_artists():
    auth_url = sp_oauth.get_authorize_url()
    print(f'Please navigate here to authorize: {auth_url}')

    response = input('Enter the URL you were redirected to: ')
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_artists(limit=20, time_range='long_term')
    
    for idx, item in enumerate(results['items']):
        artist_name = item['name']
        artist_genres = ", ".join(item['genres']) if item['genres'] else "No genres available"
        artist_popularity = item['popularity']
        print(f"{idx + 1}. {artist_name} (Genres: {artist_genres}, Popularity: {artist_popularity})")

if __name__ == '__main__':
    get_top_tracks()
    get_top_artists()