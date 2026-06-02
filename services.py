# services.py
import os
import urllib.request
import json
from models import ContentItem
import time

def load_local_environment_variables():
    """
    Scans the absolute root for the .env file to ensure it loads 
    correctly across all terminal shell instances.
    """
    # Force Python to look in the exact directory where this file lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    
    # Fallback to current working directory if not found next to services.py
    if not os.path.exists(env_path):
        env_path = ".env"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                cleaned_line = line.strip()
                if not cleaned_line or cleaned_line.startswith("#"):
                    continue
                if "=" in cleaned_line:
                    key, value = cleaned_line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

# Run the loader
load_local_environment_variables()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# High-Performance Multi-Lane Global Cache Tracking Matrix
_GLOBAL_ENGINE_CACHE = {}
CACHE_DURATION_SECONDS = 600  # Stays warm for 10 minutes to minimize network latency

def fetch_movie_trailer_embed(movie_id: int, endpoint_type: str = "movie") -> str:
    """
    Fetches genuine YouTube trailer embed strings from TMDB assets.
    """
    if not TMDB_API_KEY:
        return "https://www.youtube.com/embed/dQw4w9WgXcQ"
        
    # TV vs Movie endpoint syntax differs slightly for videos
    path_segment = "movie" if endpoint_type == "movie" else "tv"
    url = f"https://api.themoviedb.org/3/{path_segment}/{movie_id}/videos?api_key={TMDB_API_KEY}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CinevoCoreEngineV2'})
        with urllib.request.urlopen(req, timeout=4) as response:
            payload = json.loads(response.read().decode())
            videos = payload.get("results", [])

            for video in videos:
                if video.get("site") == "YouTube" and video.get("key"):
                    return f"https://www.youtube.com/embed/{video.get('key')}"
                
    except Exception:
        pass

    return "https://www.youtube.com/embed/dQw4w9WgXcQ"

def query_tmdb_pipeline(endpoint_type: str, query_params: str) -> list[ContentItem]:
    """
    A unified data stream engine that fetches, shapes, and caches pan-African 
    content matching both Movie and TV Series schemas.
    """
    global _GLOBAL_ENGINE_CACHE
    current_time = time.time()
    cache_key = f"{endpoint_type}_{query_params}"
    
    # Return from multi-lane memory cache instantly if hit and still valid
    if cache_key in _GLOBAL_ENGINE_CACHE:
        cache_data, timestamp = _GLOBAL_ENGINE_CACHE[cache_key]
        if current_time - timestamp < CACHE_DURATION_SECONDS:
            return cache_data

    if not TMDB_API_KEY:
        print(f"⚠️ Warning: TMDB_API_KEY missing! Skipping pipeline stream for: {cache_key}")
        return []

    base_segment = "discover/movie" if endpoint_type == "movie" else "discover/tv"
    url = f"https://api.themoviedb.org/3/{base_segment}?api_key={TMDB_API_KEY}&{query_params}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CinevoEnginev2'})
        with urllib.request.urlopen(req, timeout=5) as response:
            raw_data = json.loads(response.read().decode())
            results = raw_data.get("results", [])
            parsed_catalog = []

            for item_data in results[:12]:  # Top 12 records per lane for grid symmetry
                if not item_data.get('poster_path') or not item_data.get('backdrop_path'):
                    continue

                item_id = item_data.get("id")
                title = item_data.get("title") or item_data.get("name") or "UNTITLED WORK"
                release_date = item_data.get("release_date") or item_data.get("first_air_date") or "2026-01-01"
                year = int(release_date[:4]) if release_date else 2026
                
                # Fetch genuine video embed link using your core layout routine
                embed_video = fetch_movie_trailer_embed(item_id, endpoint_type)

                item = ContentItem(
                    id=item_id,
                    title=title.upper(),
                    description=item_data.get("overview", "No catalog distribution log entries configured yet."),
                    content_type="series" if endpoint_type == "tv" else "movie",
                    embedded_video_url=embed_video, 
                    poster_url=f"https://image.tmdb.org/t/p/w500{item_data.get('poster_path')}",
                    backdrop_url=f"https://image.tmdb.org/t/p/w1280{item_data.get('backdrop_path')}",
                    duration_minute=45 if endpoint_type == "tv" else 120, 
                    filmmaker_name="Pan-African Cinema",
                    release_year=year,
                    is_featured=False,
                    is_native_upload=False
                )
                parsed_catalog.append(item)
            
            # Save into localized matrix pool
            _GLOBAL_ENGINE_CACHE[cache_key] = (parsed_catalog, current_time)
            return parsed_catalog

    except Exception as e:
        print(f"⚠️ Pipeline Exception for [{cache_key}]: {e}")
        if cache_key in _GLOBAL_ENGINE_CACHE:
            return _GLOBAL_ENGINE_CACHE[cache_key][0]
        return []

# --- HIGH-LEVEL REGIONAL PAN-AFRICAN LANES ---

def fetch_external_african_movies() -> list[ContentItem]:
    """
    Keeps compatibility with main.py while fetching cross-border trending African movies.
    """
    return query_tmdb_pipeline("movie", "with_origin_country=NG|ZA|KE|GH|EG|MA&sort_by=popularity.desc")

def fetch_pan_african_movies() -> list[ContentItem]:
    """
    Queries TMDB for popular movies originating from across the African continent.
    """
    return query_tmdb_pipeline("movie", "with_origin_country=NG|ZA|KE|GH|EG|MA&sort_by=popularity.desc")

def fetch_pan_african_series() -> list[ContentItem]:
    """
    Queries TMDB for popular television and streaming shows using the TV architecture.
    """
    return query_tmdb_pipeline("tv", "with_origin_country=NG|ZA|KE|GH|EG&sort_by=popularity.desc")

def fetch_african_animations() -> list[ContentItem]:
    """
    Queries TMDB for African animated projects across the continent by tracking Genre ID 16.
    """
    return query_tmdb_pipeline("movie", "with_origin_country=NG|ZA|KE|GH|EG&with_genres=16&sort_by=popularity.desc")

def fetch_upcoming_cinema() -> list[ContentItem]:
    """
    Queries TMDB for upcoming cinema releases scheduled for late 2025/2026.
    """
    return query_tmdb_pipeline("movie", "with_origin_country=NG|ZA|KE&primary_release_date.gte=2026-01-01&sort_by=popularity.desc")

def fetch_best_by_country(country_code: str) -> list[ContentItem]:
    """
    Queries filtered movie matrices ordered by vote metrics for a specific country code (e.g., NG, ZA, KE).
    """
    return query_tmdb_pipeline("movie", f"with_origin_country={country_code.upper()}&sort_by=vote_average.desc&vote_count.gte=5")

def twelve_hours_banner_slideshow(catalog_items: list) -> list:
    """
    Selects a pool of 3 to 5 slides from trending content.
    The order/selection shifts deterministically every 12 hours.
    """
    if not catalog_items:
        return []
        
    twelve_hour_block = int(time.time() / (12 * 3600))
    pool_size = min(len(catalog_items), 5)
    slides = []
    
    for i in range(pool_size):
        item_index = (twelve_hour_block + i) % len(catalog_items)
        slides.append(catalog_items[item_index])
        
    return slides


import urllib.parse

def search_external_tmdb(query_string: str) -> list[ContentItem]:
    """
    Queries TMDB search endpoint to extract movies and series matching 
    the search token, with robust error safety and open matching fallback.
    """
    global TMDB_API_KEY
    if not TMDB_API_KEY:
        TMDB_API_KEY = os.getenv("TMDB_API_KEY")
        
    if not TMDB_API_KEY:
        print("⚠️ Search Engine Error: TMDB_API_KEY environment variable missing!")
        return []
        
    encoded_query = urllib.parse.quote(query_string)
    
    # Using dynamic multi-search to handle movies and shows alike
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={encoded_query}&include_adult=false"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CinevoCoreSearchV2'})
        with urllib.request.urlopen(req, timeout=5) as response:
            raw_data = json.loads(response.read().decode())
            results = raw_data.get("results", [])
            parsed_results = []
            
            for raw in results[:15]: 
                media_type = raw.get("media_type")
                if media_type not in ["movie", "tv"]:
                    continue
                    
                # Skip broken records missing primary imagery assets
                if not raw.get('poster_path'):
                    continue

                title = raw.get("title") or raw.get("name") or "UNTITLED MATCH"
                release_date = raw.get("release_date") or raw.get("first_air_date") or "2026"
                year = int(release_date[:4]) if len(release_date) >= 4 else 2026
                
                item = ContentItem(
                    id=raw.get("id"),
                    title=title.upper(),
                    description=raw.get("overview", "No catalog logging documentation provided yet."),
                    content_type="series" if media_type == "tv" else "movie",
                    embedded_video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                    poster_url=f"https://image.tmdb.org/t/p/w500{raw.get('poster_path')}",
                    backdrop_url=f"https://image.tmdb.org/t/p/w1280{raw.get('backdrop_path') or raw.get('poster_path')}",
                    duration_minute=120,
                    filmmaker_name="Cinema Hub Networks",
                    release_year=year,
                    is_featured=False,
                    is_native_upload=False
                )
                parsed_results.append(item)
                
            return parsed_results
            
    except Exception as e:
        print(f"⚠️ Search Pipeline Exception for query '{query_string}': {e}")
        return []

