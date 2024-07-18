from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('main', __name__)

CACHE_PATH = '.spotipyoauthcache'

sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope='user-top-read',
    cache_path=CACHE_PATH
)

@bp.route('/')
def home():
    print("Accessed home route")
    token_info = session.get("token_info", None)
    if token_info:
        print(f"Token Info in Home: {token_info}")
    return render_template('home.html')

@bp.route('/login')
def login():
    print("Accessed login route")
    auth_url = sp_oauth.get_authorize_url()
    print(f"Auth URL: {auth_url}")  # Debug print
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    print("Accessed callback route")
    session.clear()
    code = request.args.get('code')
    print(f"Code received: {code}")
    
    if not code:
        print("Missing code parameter")
        return "Missing code parameter", 400
    try:
        token_info = sp_oauth.get_access_token(code)
        print(f"Token info received: {token_info}")
    except Exception as e:
        print(f"Error getting token info: {e}")
        return "Error getting token info", 500

    if not token_info:
        print("Failed to receive token info")
        return "Failed to receive token info", 400

    session["token_info"] = token_info
    sp_oauth.cache_path = CACHE_PATH
    sp_oauth.save_token_info(token_info)
    print(f"Session updated with token info: {session.get('token_info')}")

    return redirect(url_for('main.results'))

@bp.route('/results')
def results():
    print("Accessed results route")
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        print("No cached token, redirecting to login")
        return redirect(url_for('.login'))
    
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session["token_info"] = token_info
        sp_oauth.cache_path = CACHE_PATH
        sp_oauth.save_token_info(token_info)
    
    sp = spotipy.Spotify(auth=token_info['access_token'])

    try:
        top_artists = sp.current_user_top_artists(limit=10, time_range='long_term')['items']
        top_tracks = sp.current_user_top_tracks(limit=10, time_range='long_term')['items']
        print(f"Top artists: {top_artists}")
        print(f"Top tracks: {top_tracks}")

        return render_template('results.html', top_artists=top_artists, top_tracks=top_tracks)
    except Exception as e:
        print(f"Error fetching data from Spotify: {e}")
        return "Error fetching data from Spotify", 500
