from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Dict, Any, Optional

from app.db.session import get_db
from app.models.url import URLMapping
from app.models.click import ClickEvent
from app.schemas.analytics import (
    URLAnalyticsResponse,
    ClickDateStat,
    BreakdownStat,
)
from app.security.auth import get_optional_token_claims, verify_resource_ownership

router = APIRouter(tags=["Analytics & Metrics"])


@router.get(
    "/stats/{code}",
    response_model=URLAnalyticsResponse,
    summary="Get privacy-preserving analytics for a shortened URL"
)
def get_url_analytics(
    code: str,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_token_claims),
    db: Session = Depends(get_db)
):
    """
    Retrieves analytics metrics for a short code.
    
    Security & Access Control Rules:
    - If URL was created by a registered user, ONLY the creator (or admin) can view analytics (prevents IDOR).
    - If URL was created anonymously, basic aggregate stats are viewable.
    - All analytics protect user privacy: individual IPs are never exposed.
    """
    # 1. Fetch URL mapping
    url_mapping = db.query(URLMapping).filter(URLMapping.short_code == code).first()
    if not url_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL code '{code}' not found."
        )

    # 2. Access control check
    if url_mapping.created_by:
        current_user_id = claims.get("sub") if claims else None
        is_admin = (claims.get("tier") == "admin") if claims else False
        verify_resource_ownership(url_mapping.created_by, current_user_id, is_admin)

    # 3. Aggregations (Matching Member 1's SQL analytics queries)
    # Total clicks
    total_clicks = db.query(func.count(ClickEvent.id)).filter(
        ClickEvent.url_mapping_id == url_mapping.id
    ).scalar() or 0

    # Unique clicks (by salted ip_hash)
    unique_clicks = db.query(func.count(distinct(ClickEvent.ip_hash))).filter(
        ClickEvent.url_mapping_id == url_mapping.id
    ).scalar() or 0

    # Clicks over time
    date_records = (
        db.query(
            func.date(ClickEvent.clicked_at).label("click_date"),
            func.count(ClickEvent.id).label("total"),
            func.count(distinct(ClickEvent.ip_hash)).label("unique")
        )
        .filter(ClickEvent.url_mapping_id == url_mapping.id)
        .group_by(func.date(ClickEvent.clicked_at))
        .order_by("click_date")
        .all()
    )
    clicks_over_time = [
        ClickDateStat(
            click_date=str(r.click_date),
            total_clicks=r.total,
            unique_clicks=r.unique
        )
        for r in date_records
    ]

    # Device breakdown
    device_records = (
        db.query(
            ClickEvent.device_type,
            func.count(ClickEvent.id).label("clicks")
        )
        .filter(ClickEvent.url_mapping_id == url_mapping.id)
        .group_by(ClickEvent.device_type)
        .order_by(func.count(ClickEvent.id).desc())
        .all()
    )
    device_breakdown = [
        BreakdownStat(category=r.device_type or "Unknown", clicks=r.clicks)
        for r in device_records
    ]

    # Referrer breakdown
    referrer_records = (
        db.query(
            ClickEvent.referrer,
            func.count(ClickEvent.id).label("clicks")
        )
        .filter(ClickEvent.url_mapping_id == url_mapping.id)
        .group_by(ClickEvent.referrer)
        .order_by(func.count(ClickEvent.id).desc())
        .limit(10)
        .all()
    )
    referrer_breakdown = [
        BreakdownStat(category=r.referrer or "Direct / None", clicks=r.clicks)
        for r in referrer_records
    ]

    # Country breakdown
    country_records = (
        db.query(
            ClickEvent.country_code,
            func.count(ClickEvent.id).label("clicks")
        )
        .filter(ClickEvent.url_mapping_id == url_mapping.id)
        .group_by(ClickEvent.country_code)
        .order_by(func.count(ClickEvent.id).desc())
        .limit(10)
        .all()
    )
    country_breakdown = [
        BreakdownStat(category=r.country_code or "Unknown", clicks=r.clicks)
        for r in country_records
    ]

    return URLAnalyticsResponse(
        short_code=url_mapping.short_code,
        total_clicks=total_clicks,
        unique_clicks=unique_clicks,
        clicks_over_time=clicks_over_time,
        device_breakdown=device_breakdown,
        referrer_breakdown=referrer_breakdown,
        country_breakdown=country_breakdown
    )

