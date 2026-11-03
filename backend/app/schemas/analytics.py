from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ClickDateStat(BaseModel):
    click_date: str
    total_clicks: int
    unique_clicks: int


class BreakdownStat(BaseModel):
    category: str
    clicks: int


class URLAnalyticsResponse(BaseModel):
    short_code: str
    total_clicks: int
    unique_clicks: int
    clicks_over_time: List[ClickDateStat]
    device_breakdown: List[BreakdownStat]
    referrer_breakdown: List[BreakdownStat]
    country_breakdown: List[BreakdownStat]

