import spotipy
import requests
import os
import random
import datetime
import pandas as pd

# Function to refresh access token
def refresh_access_token(refresh_token):
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    auth_header = {'Authorization': 'Basic ' + (client_id + ':' + client_secret).encode().base64()}
    response = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=auth_header)
    return response.json().get('access_token')

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
refresh_token = os.environ['SPOTIPY_REFRESH_TOKEN']
new_access_token = refresh_access_token(refresh_token)

# Set up Spotipy
sp = spotipy.Spotify(auth=new_access_token)

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