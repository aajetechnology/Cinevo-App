# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_
from typing import List, Dict, Any

from database import engine, init_db, get_session
from models import ContentItem, Series
from services import fetch_external_african_movies, twelve_hours_banner_slideshow
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import services

app = FastAPI(title="Cinevo Platform Core Backend Matrix v2")

@app.on_event("startup")
def on_startup():
    """Ensures database schemas are active the millisecond the server boots."""
    init_db()
    print("🚀 Cinevo Core Engine Operational. Tables verified.")

# =========================================================================
# 🛠️ NATIVE PLATFORM MANAGEMENT ENDPOINTS (UPLOAD ENGINE OPERATIONS)
# =========================================================================

@app.post("/api/admin/upload-content", response_model=ContentItem, status_code=status.HTTP_201_CREATED)
def upload_native_content(item: ContentItem, session: Session = Depends(get_session)):
    """
    Saves new Feature Movies, Short Films, or Series Episodes directly to our local database storage.
    """
    # Defensive logic: If item is marked as featured, remove old feature highlights to keep the spotlight clean
    if item.is_featured:
        old_features = session.exec(select(ContentItem).where(ContentItem.is_featured == True)).all()
        for old_item in old_features:
            old_item.is_featured = False
            session.add(old_item)
            
    item.is_native_upload = True # Hardcode safety lock for admin uploads
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.post("/api/admin/create-series", response_model=Series, status_code=status.HTTP_201_CREATED)
def create_native_series(series: Series, session: Session = Depends(get_session)):
    """
    Initializes a parent container series record entry (e.g., Animation series projects).
    """
    session.add(series)
    session.commit()
    session.refresh(series)
    return series

# =========================================================================
# 📡 DYNAMIC CATLOG GENERATION MATRIX
# =========================================================================

@app.get("/api/catalog")
def get_integrated_dashboard_catalog(session: Session = Depends(get_session)):
    """
    Consolidates active custom native platform database entries with live 
    external network data streams from TMDB.
    """
    uploaded_movies = session.exec(select(ContentItem).where((ContentItem.content_type == "movie") & (ContentItem.is_native_upload == True))).all()
    uploaded_shorts = session.exec(select(ContentItem).where((ContentItem.content_type == "short") & (ContentItem.is_native_upload == True))).all()
    uploaded_series = session.exec(select(Series)).all()


    african_movies = services.fetch_pan_african_movies()
    african_series = services.fetch_pan_african_series()
    african_animations = services.fetch_african_animations()
    upcoming_releases = services.fetch_upcoming_cinema()
    

    best_of_nigeria = services.fetch_best_by_country("NG")
    best_of_south_africa = services.fetch_best_by_country("ZA")
    best_of_kenya = services.fetch_best_by_country("KE")

    # 1. Gather spotlight featured showcase record
    banner_slideshow = services.twelve_hours_banner_slideshow(african_movies)

    # 4. Synthesize Combined Rows (Native + Global API Streams)
    consolidated_movies = uploaded_movies + african_movies
    consolidated_series = [s.dict() for s in uploaded_series] + [item.dict() if hasattr(item, 'dict') else item for item in african_series]

    return {
        "banner_slideshow": [item.dict() if hasattr(item, 'dict') else item for item in banner_slideshow],
        "popular_movies": [item.dict() if hasattr(item, 'dict') else item for item in consolidated_movies],
        "popular_series": consolidated_series,
        "african_animations": [item.dict() if hasattr(item, 'dict') else item for item in african_animations],
        "upcoming_cinema": [item.dict() if hasattr(item, 'dict') else item for item in upcoming_releases],
        "african_shorts_row": [item.dict() for item in uploaded_shorts],
        "best_of_nigeria": [item.dict() if hasattr(item, 'dict') else item for item in best_of_nigeria],
        "best_of_south_africa": [item.dict() if hasattr(item, 'dict') else item for item in best_of_south_africa],
        "best_of_kenya": [item.dict() if hasattr(item, 'dict') else item for item in best_of_kenya]
    }


app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def serve_dashboard_home():
    return FileResponse("static/index.html")


@app.get("/admin")
def serve_admin_panel():
    return FileResponse("static/admin.html")


@app.get("/movies")
def serve_movies_page():
    return FileResponse("static/movies.html")

@app.get("/series")
def serve_series_page():
    return FileResponse("static/series.html") 

@app.get("/shorts")
def serve_shorts_page():
    return FileResponse("static/shorts.html")
@app.get("/api/search")
def search_platform_catalog(q: str = "", session: Session = Depends(get_session)):
    """
    Exposes high-performance case-insensitive relational text matching vectors.
    Returns matched results filtered cleanly by content structural rules.
    """
    if not q or len(q.strip()) == 0:
        return {"movies": [], "series": []}
        
    query_string = f"%{q.strip()}%"
    
    # Query database records utilizing case-insensitive lookahead conditions
    matched_items = session.exec(
        select(ContentItem).where(
            (ContentItem.title.like(query_string)) | 
            (ContentItem.description.like(query_string)) |
            (ContentItem.filmmaker_name.like(query_string))
        )
    ).all()
    
    matched_series = session.exec(
        select(Series).where(
            (Series.title.like(query_string)) | 
            (Series.description.like(query_string)) |
            (Series.studio_name.like(query_string))
        )
    ).all()
    
    return {
        "movies": matched_items,
        "series": matched_series
    }

@app.get("/api/search")
def search_catalog(q: str = Query(..., min_length=1), session: Session = Depends(get_session)):
    """
    Highly resilient search route. Searches local data but safely catches 
    empty tables or exceptions so live TMDB network results always pass through.
    """
    clean_query = q.strip().lower()
    combined_results = []
    
    # 1. Safe Search Native Tables
    try:
        native_items = session.exec(
            select(ContentItem).where(
                or_(
                    ContentItem.title.contains(clean_query),
                    ContentItem.description.contains(clean_query)
                )
            )
        ).all()
        for item in native_items:
            combined_results.append(item.dict())
    except Exception as db_err:
        print(f"ℹ️ Local database search bypassed or table empty: {db_err}")

    # 2. Search External TMDB Live Streams
    try:
        external_results = services.search_external_tmdb(clean_query)
        existing_ids = {x["id"] for x in combined_results}
        
        for item in external_results:
            if item.id not in existing_ids:
                combined_results.append(item.dict())
    except Exception as api_err:
        print(f"⚠️ Live TMDB API Search Failed: {api_err}")

    return {"results": combined_results}



