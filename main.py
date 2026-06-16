import csv
import requests
from base64 import b64encode
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()


def get_env_vars(var_name):
    """
    Retrieve an environment variable by name, raising EnvironmentError if not set.
    """

    var = os.getenv(var_name)
    if var is None:
        raise EnvironmentError(f"Env var {var_name} not defined")

    return var


# POST method on Spotify to get token url (OAuth2.0) for GET method
def get_access_token():
    """
    Request a client credentials OAuth2.0 access token from the Spotify API.
    Reads CLIENT_ID, CLIENT_SECRET, and TOKEN_URL from environment variables,
    encodes them as Base64 for Basic auth, and returns the full token response dict
    (which includes the access_token and expires_in fields).
    """
    try:
        client_id = get_env_vars("CLIENT_ID")
        client_secret = get_env_vars("CLIENT_SECRET")
        token_url = get_env_vars("TOKEN_URL")

        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = b64encode(auth_bytes).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "client_credentials",
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        response_data = response.json()
        pprint(response_data)
        return response_data

    except requests.HTTPError as e:
        print(f"HTTP error fetching access token: {e}")

    except EnvironmentError as e:
        print(f"Missing environment variable: {e}")


# GET method to get album
def get_album_data(access_token, album_id, page_size=5):
    """
    Fetch album metadata and all tracks from the Spotify API.
    Paginates through the tracks endpoint using page_size as the chunk size,
    collecting every track regardless of how many pages are needed.
    Returns the album dict with tracks.items containing the full track list.
    """

    url_album = f"https://api.spotify.com/v1/albums/{album_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    try:
        response = requests.get(url_album, headers=headers, params={"limit": page_size})
        response.raise_for_status()
        album_data = response.json()

        all_tracks = album_data["tracks"]["items"]
        next_url = album_data["tracks"].get("next")

        while next_url:
            response = requests.get(next_url, headers=headers)
            response.raise_for_status()
            page = response.json()
            all_tracks.extend(page["items"])
            next_url = page.get("next")

        album_data["tracks"]["items"] = all_tracks
        return album_data

    except requests.HTTPError as e:
        print(f"HTTP error fetching album data: {e}")

    except requests.RequestException as e:
        print(f"Error connecting to Spotify API: {e}")


def process_album_data(album_data):
    """
    Flatten the raw Spotify album JSON into a list of track-level dicts.
    Each dict contains album-level fields (name, artists, release_date, total_tracks)
    combined with track-level fields (track_number, track_name, track_artists,
    duration_ms, explicit). Returns an empty list if album_data is None or empty.
    """
    if not album_data:
        return []

    album_name = album_data.get("name", "")
    release_date = album_data.get("release_date", "")
    total_tracks = album_data.get("total_tracks", 0)
    artists = ", ".join(artist["name"] for artist in album_data.get("artists", []))

    tracks = []
    for track in album_data.get("tracks", {}).get("items", []):
        track_artists = ", ".join(artist["name"] for artist in track.get("artists", []))
        tracks.append(
            {
                "album_name": album_name,
                "album_artists": artists,
                "release_date": release_date,
                "total_tracks": total_tracks,
                "track_number": track.get("track_number"),
                "track_name": track.get("name"),
                "track_artists": track_artists,
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit"),
            }
        )

    # print(tracks)
    return tracks


def save_csv(tracks, filename="album_tracks.csv"):
    """
    Write the processed track list to a CSV file.
    Takes the list of track dicts returned by process_album_data() and writes
    them to a CSV file.
    Column order matches the dict key order.
    """
    if not tracks:
        print("No tracks to save.")
        return

    fieldnames = tracks[0].keys()

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        # Creates a writer that knows how to turn a dict into a CSV row, using fieldnames to define the column order.
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Writes the first row, the header
        writer.writeheader()

        # Writes the data
        writer.writerows(tracks)

    print(f"Saved {len(tracks)} tracks to {filename}")


if __name__ == "__main__":

    token_data = get_access_token()
    access_token = token_data["access_token"]

    album_id = "4aawyAB9vmqN3uQ7FjRGTy"
    album_data = get_album_data(access_token, album_id, page_size=5)

    tracks = process_album_data(album_data)
    save_csv(tracks)
