from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import json
from collections import deque
import time
import os
import dotenv
from pathlib import Path

env_path = Path('.') / '.env'
dotenv.load_dotenv()

class Traversals:
    def __init__(self, web={}):
        self.web = web
    def findDistance(self, start, target):
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
                artist_obj = self.web.get(artist, {})
                related = artist_obj.get("related", [])
                for related_artist in related:
                    path.append(related_artist)
                    queue.append((related_artist, index+1, path.copy()))
                    path.pop()
        return None

    def getConnected(self, artist):
        queue = deque([])
        result = []
        queue.append(artist)
        visited = set()
        while queue:
            artist = queue.popleft()
            if artist not in visited:
                result.append(artist)
                visited.add(artist)
                artist_obj = self.web.get(artist, {})
                related = artist_obj.get("related", [])
                for related_artist in related:
                    queue.append(related_artist)
        return result

class SpotifyClient:
    def __init__(self, web=None):
        self.client: Spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.environ["SPOTIFY_CLIENT_ID"], client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]))
        self.web = {}
        with open("public/data/new_output.json", "r") as infile:
            self.web = json.load(infile)

    def getAlbumTracks(self, album_id):
        artists_on_album = set()
        time.sleep(1)
        album_tracks = self.client.album_tracks(album_id)
        for track_information in album_tracks["items"]:
            for artist in track_information["artists"]:
                artists_on_album.add(artist["name"])
        return list(artists_on_album)

    def getAlbums(self, artist_id):
        connected_artists = []
        time.sleep(1)
        artist_albums = self.client.artist_albums(artist_id)
        for album_information in artist_albums["items"]:
            if album_information.get("album_group", "") in ["album", "single"]:
                artists_on_album = self.getAlbumTracks(album_information["id"])
                connected_artists.extend(artists_on_album)
        return list(set(connected_artists))

    def getConnectedArtists(self, artists):
        for artist, artist_information in artists.items():
            connected_artists = self.getAlbums(artist_information["id"], self.client)
            artists[artist]["connected"] = connected_artists
        return artists

    def getPopularArtists(self):
        valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        artists = {}
        for character in valid_chars:
            artists = self.searchNewArtists(artists, character)
            for character_2 in valid_chars:
                artists = self.searchNewArtists(artists, character+character_2)
                artists = self.searchNewArtists(artists, character+character_2, offset=50)
        return artists

    def searchNewArtists(self, artists, query, popularity_threshold=50, limit=50, offset=0):
        time.sleep(1)
        results = self.client.search(f"artist:{query}", type="artist", limit=limit, offset=offset)
        for artist_information in results["artists"]["items"]:
            if artist_information["name"] in artists or int(artist_information["popularity"]) < popularity_threshold:
                continue
            print(f'{artist_information["name"]} - {artist_information["popularity"]}')
            artists[artist_information["name"]] = {"id": artist_information["id"], "name": artist_information["name"], "popularity": artist_information["popularity"], "image": artist_information["images"][0]["url"]}
        return artists
    
    def getArtistInformation(self, artist_id):
        time.sleep(1)
        artistTopTracksInformation = self.client.artist_top_tracks(artist_id)
        topTrack = artistTopTracksInformation["tracks"][0]
        time.sleep(1)
        relatedArtists = self.client.artist_related_artists(artist_id)
        return {
            "related": [artist["name"] for artist in relatedArtists["artists"] if artist["name"] in self.web],
            "top_song_preview_url": topTrack["preview_url"],
            "top_song_name": topTrack["name"],
            "top_song_id": topTrack["id"],
            "top_song_art": "https://i.scdn.co/image/ab67616d0000b273357a322c96a9c629de19ed1e"
        }
    
    def updateWithArtistInformation(self, artists):
        for artist, artist_information in artists.items():
            new_artist_information = self.getArtistInformation(artist_information["id"])
            for key, value in new_artist_information.items():
                self.web[artist][key] = value
        return artists
            

    def writeOutputToFile(self):
        artists = self.getPopularArtists()
        updated_artists = self.updateWithArtistInformation(artists)
        updated_artists_with_connected = self.getConnectedArtists(updated_artists)
        with open("public/data/new_output.json", "w") as outfile:
            json.dump(updated_artists_with_connected, outfile)
        for existing_artist in self.web:
            if not existing_artist in artists:
                print(existing_artist)

def main():
    spotifyClient = SpotifyClient()
    spotifyClient.writeOutputToFile()

main()