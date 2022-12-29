import ytmusicapi
import spotipy
import argparse

# Replace these with your API keys
spotify_client_id = '<your_spotify_client_id>'
spotify_client_secret = '<your_spotify_client_secret>'
youtube_music_api_key = '<your_youtube_music_api_key>'

# Authenticate with the Spotify API
spotify = spotipy.Spotify(client_id=spotify_client_id, client_secret=spotify_client_secret)

# Authenticate with the YouTube Music API
ytmusic = ytmusicapi.YouTubeMusic(api_key=youtube_music_api_key)

def convert_from_spotify(playlist_name):
    # Retrieve your playlists from Spotify
    spotify_playlists = spotify.current_user_playlists()

    # Find the playlist with the specified name
    playlist = next((p for p in spotify_playlists['items'] if p['name'] == playlist_name), None)
    if playlist is None:
        raise ValueError(f'Playlist with name "{playlist_name}" not found in Spotify')

    # Add the playlist to YouTube Music, if doesnt exist
    # Retrieve your playlists from YouTube Music
    ytmusic_playlists = ytmusic.playlists()

    # Find the playlist with the specified name  
    ytmusic_playlist = next((p for p in ytmusic_playlists if p['name'] == playlist_name), None)

    if ytmusic_playlist is None:
        ytmusic_playlist = ytmusic.add_playlist(playlist['name'])

    # Create list of tracks from Spotify playlist to transfer
    tracks = spotify.playlist_tracks(playlist['id'])

    # Add the tracks to the new playlist
    ytmusic.add_tracks(ytmusic_playlist['id'], [track['track']['id'] for track in tracks['items']])

def convert_from_ytmusic(playlist_name):
    # Retrieve your playlists from YouTube Music
    ytmusic_playlists = ytmusic.playlists()

    # Find the playlist with the specified name
    playlist = next((p for p in ytmusic_playlists if p['name'] == playlist_name), None)
    if playlist is None:
        raise ValueError(f'Playlist with name "{playlist_name}" not found in YouTube Music')


    spotify_playlists = spotify.current_user_playlists()

    # Find the playlist with the specified name
    spotify_playlist = next((p for p in spotify_playlists['items'] if p['name'] == playlist_name), None)
    if spotify_playlist is None:
        # Add the playlist to Spotify if it doesn't exist
        spotify_playlist = spotify.user_playlist_create(user=spotify.me()['id'], name=playlist['name'])
        
    # Get the tracks in the playlist
    tracks = ytmusic.playlist_items(playlist['id'])

    # Add the tracks to the playlist
    spotify.user_playlist_add_tracks(user=spotify.me()['id'], playlist_id=spotify_playlist['id'], tracks=[track['track']['id'] for track in tracks])

# Use argparse to parse the command-line arguments
parser = argparse.ArgumentParser(description='Convert playlist between Spotify and YouTube Music')
parser.add_argument('-o', '--origin', required=True, choices=['spotify', 'ytmusic'], help='origin service')
parser.add_argument('playlist_name', required=True, help='name of the playlist to copy/update')

args = parser.parse_args()

# Convert the playlist based on the origin service
if args.origin == 'spotify':
    convert_from_spotify(playlist_name)
elif args.origin == 'ytmusic':
    convert_from_ytmusic(playlist_name)
