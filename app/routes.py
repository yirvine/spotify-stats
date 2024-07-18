from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import asyncio
import os
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from flask import send_from_directory


load_dotenv()

bp = Blueprint('main', __name__)

sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope='user-top-read',
    cache_path='CACHE_PATH'
)

@bp.route('/')
def home():
    print("Home route accessed")
    token_info = session.get("token_info", None)
    if token_info:
        print(f"Token Info in Home: {token_info}")
    return render_template('home.html')

@bp.route('/login')
def login():
    print("Login route accessed")
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    print("Callback route accessed")
    session.clear()
    code = request.args.get('code')
    print("Code received:", code)
    
    if not code:
        return "Missing code parameter", 400
    try:
        token_info = sp_oauth.get_access_token(code)
        print("Token info received:", token_info)
    except Exception as e:
        print("Error getting token info:", e)
        return "Error getting token info", 500

    if not token_info:
        return "Failed to receive token info", 400

    session["token_info"] = token_info
    print("Session updated with token info:", session.get("token_info"))
    return redirect(url_for('main.playlists'))

@bp.route('/top-artists')
def top_artists():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('.login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_artists(limit=10, time_range='long_term')
    return render_template('top_artists.html', artists=results['items'])

@bp.route('/top-tracks')
def top_tracks():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('.login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_tracks(limit=10, time_range='long_term')
    return render_template('top_tracks.html', tracks=results['items'])
