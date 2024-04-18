from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import json
from collections import deque
import time

def findDistance(start, target, web):
    queue = deque([])
    index = 0
    queue.append((start, index, [start]))
    visited = set()
    while queue:
        artist, index, path = queue.popleft()
        if artist == target:
            return index, path
        if artist not in visited:
            visited.add(artist)
            artist_obj = web.get(artist, {})
            related = artist_obj.get("related", [])
            for related_artist in related:
                path.append(related_artist)
                queue.append((related_artist, index+1, path.copy()))
                path.pop()
    return None

def getConnected(artist, web):
    queue = deque([])
    result = []
    queue.append(artist)
    visited = set()
    while queue:
        artist = queue.popleft()
        if artist not in visited:
            result.append(artist)
            visited.add(artist)
            artist_obj = web.get(artist, {})
            related = artist_obj.get("related", [])
            for related_artist in related:
                queue.append(related_artist)
    return result

def getAlbumTracks(album_id, client: Spotify):
    artists_on_album = set()
    time.sleep(10)
    album_tracks = client.album_tracks(album_id)
    for track_information in album_tracks["items"]:
        for artist in track_information["artists"]:
            artists_on_album.add(artist["name"])
    return list(artists_on_album)

def getAlbums(artist_id, client: Spotify):
    connected_artists = []
    time.sleep(10)
    artist_albums = client.artist_albums(artist_id)
    for album_information in artist_albums["items"]:
        if album_information.get("album_group", "") in ["album", "single"]:
            artists_on_album = getAlbumTracks(album_information["id"], client)
            connected_artists.extend(artists_on_album)
    return list(set(connected_artists))

def getConnectedArtists(client: Spotify, web):
    for artist, artist_information in list(web.items()):
        connected_artists = getAlbums(artist_information["id"], client)
        web[artist]["connected"] = connected_artists
    return web

def getPopularArtists(client: Spotify):
    valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    artists = {}
    for character in valid_chars:
        artists = searchNewArtists(client, artists, character)
        for character_2 in valid_chars:
            artists = searchNewArtists(client, artists, character+character_2)
    return artists

def searchNewArtists(client: Spotify, artists, query, popularity_threshold=50):
    time.sleep(1)
    results = client.search(f"artist:{query}", type="artist", limit=50, offset=0)
    for artist_information in results["artists"]["items"]:
        if artist_information["name"] in artists or int(artist_information["popularity"]) < popularity_threshold:
            continue
        print(f'{artist_information["name"]} - {artist_information["popularity"]}')
        artists[artist_information["name"]] = {"id": artist_information["id"], "name": artist_information["name"], "popularity": artist_information["popularity"]}
    return artists

def main():
    client = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id="f5e75e463a4e4f539259a69cbd303cb3", client_secret="3683a40eeeb648c282d1b86675d093c0"))
    web = {}
    with open("public/data/web.json", "r") as infile:
        web = json.load(infile)
        
    artists = getPopularArtists(client)
    
    with open("public/data/new_output.json", "w") as outfile:
        json.dump(artists, outfile)
    # with open("new_output.json", "r") as infile:
    #     web = json.load(infile)
    
    for i in web:
        if not i in artists:
            print(i)

main()