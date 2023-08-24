import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import datetime
import pandas as pd

# Read credentials from text file
with open('credentials.txt', 'r') as file:
    lines = file.readlines()
    client_id = lines[0].strip()
    client_secret = lines[1].strip()

# Set up spotipy
# Note: I have set up a redirect URI in my Spotify developer dashboard
# See https://community.spotify.com/t5/Spotify-for-Developers/Redirect-URI-needed/td-p/5067419
# for a discussion on why this is necessary and why to use localhost:8000
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:8000/", scope="playlist-modify-public user-library-read user-read-recently-played"))

# Get all liked songs
# Since i have over 3000 songs, i need to get them in batches
# Spotify's API only allows upto 50 songs at a time
offset = 0
liked_songs = []
while True:
    batch = sp.current_user_saved_tracks(offset=offset)
    liked_songs += batch['items']
    if batch['next'] is None:
        break
    offset += len(batch['items'])
    
# Filter songs added more than 90 days ago and create weighted list
# I am choosing three months as my cutoff but you can choose whatever you want
weighted_songs = []
for song in liked_songs:
    added_date = datetime.datetime.strptime(song['added_at'], "%Y-%m-%dT%H:%M:%SZ")
    added_date = added_date.replace(tzinfo=datetime.timezone.utc)  # Add UTC timezone information
    age_days = (datetime.datetime.now(datetime.timezone.utc) - added_date).days
    
    if age_days > 90:
        # Below I simply use the age in days as the weight
        # this is going to repeat the songs as many days old it is
        # there are other ways to do this, but this is the simplest
        weighted_songs += [song['track']['id']] * age_days
        
# Shuffle the weighted list and select the top 100 (or desired number)
random.shuffle(weighted_songs)
selected_tracks = weighted_songs[:100]


# get names of selected tracks
selected_tracks_names = [sp.track(track_id)['name'] for track_id in selected_tracks]
selected_tracks_names

# Store these selected tracks in a CSV file for record keeping
# Save a pandas data frame with selected tracks and a today's date and time as a CSV file
df = pd.DataFrame({'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),     
              'track_name': selected_tracks_names,
              'track_id': selected_tracks})

# if df exists, append to it
# if not, create it
def append_to_csv(df):
    try:
        existing_df = pd.read_csv('selected_tracks.csv')
        df = pd.concat([existing_df, df])
    except:
        pass
    df.to_csv('selected_tracks.csv', index=False)
    
append_to_csv(df)

# Finally...
# Create a new playlist
user_id = sp.me()['id']
playlist = sp.user_playlist_create(user_id, 'random', public=True, description="This week's random songs that I haven't listened in a while")

# Add selected tracks to the new playlist
sp.playlist_add_items(playlist['id'], selected_tracks)