# Randomized Spotify Playlist Creator


## Overview
This repository contains a Python script that automates the creation of a randomized Spotify playlist from the songs you have liked but haven't played in the last 90 days. The songs are selected with weights, where older songs are more likely to be chosen, and a new playlist of 100 songs is created. 

The script is set to run automatically every Monday using GitHub Actions.

See details at https://www.harsh17.in/spotify-randomizer/

## How It Works
1. **Fetching Liked Songs:** The script fetches all the songs that you've liked on Spotify.
2. **Filtering Songs:** Only the songs that were added to your liked songs more than 90 days ago are considered.
3. **Weighted Shuffling:** The songs are shuffled with weights according to their age, with older songs being more likely to be selected.
4. **Creating a Playlist:** A new playlist called "random" is created, and the selected 100 songs are added to it.

## Usage
If you want to use this script, you'll need to make the following modifications:

### Spotify Credentials
You'll need to provide your Spotify Client ID and Client Secret. These should be added to GitHub Secrets with the names SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.

### GitHub Actions
The script is set to run automatically every Monday using GitHub Actions. You can find the workflow configuration in the `.github/workflows directory`. You can modify the cron schedule or other workflow settings as needed.

### Python Script
The main logic is contained in `script.py`. You may need to modify this file to suit your preferences or specific use case.



