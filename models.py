from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime




class ContentItem(SQLModel, table=True):
    """Unified relational schema for standalone movies, series, episodes,
    documentaries, and short films"""

    id:Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    content_type: str
    embedded_video_url: str
    poster_url: str
    backdrop_url: str
    duration_minute: int
    filmmaker_name: str
    release_year: int
    is_featured: bool = Field(default=False)
    is_native_upload: bool = Field(default=False)
    series_id:Optional[int] = Field(default=None, foreign_key="series.id")
    season_number: Optional[int] = Field(default=None)
    episode_number: Optional[int] = Field(default=None)

    created_at:datetime = Field(default_factory=datetime.utcnow)


class Series(SQLModel, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    poster_url: str
    backdeop_url: str
    studio_name: str
    release_year: int
    created_at:datetime = Field(default_factory=datetime.utcnow)