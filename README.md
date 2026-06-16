# Spotify Album API

A simple Python script that fetches album data from the Spotify Web API and exports it to a CSV file.

## What it does

1. Authenticates with the Spotify API using OAuth2.0 Client Credentials
2. Fetches album metadata for a given album ID
3. Flattens the data into one row per track
4. Saves the result to `album_tracks.csv`

## Output

Each row in the CSV represents one track with the following columns:

| Column | Description |
|---|---|
| `album_name` | Name of the album |
| `album_artists` | Album-level artist(s) |
| `release_date` | Album release date |
| `total_tracks` | Total number of tracks on the album |
| `track_number` | Position of the track on the album |
| `track_name` | Name of the track |
| `track_artists` | Track-level artist(s) |
| `duration_ms` | Track duration in milliseconds |
| `explicit` | Whether the track has explicit content |

## Setup

### 1. Create a Spotify app

Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), create an app, and copy your **Client ID** and **Client Secret**.

### 2. Configure environment variables

Create a `.env` file in the project root:

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
TOKEN_URL=https://accounts.spotify.com/api/token
```

### 3. Install dependencies

```bash
pip install requests python-dotenv
```

Or with `uv`:

```bash
uv sync
```

## Usage

Set the `album_id` in `main.py` to the Spotify album ID you want to export, then run:

```bash
python main.py
```

The album ID is the last part of a Spotify album URL:
```
https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy
                                    ^^^^^^^^^^^^^^^^^^^^^^
```

The output file `album_tracks.csv` will be created in the project directory.
