"""Backend agents package"""
from backend.agents.realtime_agent import (
    RealtimeAgent,
    ArxivAgent,
    NewsAgent,
    WikipediaAgent,
    DataSourceAggregator
)

__all__ = [
    'RealtimeAgent',
    'ArxivAgent',
    'NewsAgent',
    'WikipediaAgent',
    'DataSourceAggregator'
]
