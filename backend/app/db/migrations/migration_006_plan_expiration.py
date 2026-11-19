"""Normalize legacy plans and cap previously unexpired links by plan."""

from datetime import timedelta

from app.db.session import SessionLocal
from app.models.url import URLMapping
from app.models.user import User
from app.services.plans import MAX_LINK_DAYS, normalize_tier


def migrate() -> int:
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            if user.tier == "registered":
                user.tier = "free"
            elif user.tier == "premium":
                user.tier = "pro"

        tiers_by_user = {user.id: normalize_tier(user.tier) for user in users}
        updated_links = 0
        links = db.query(URLMapping).all()
        for link in links:
            tier = tiers_by_user.get(link.created_by, "free")
            max_days = MAX_LINK_DAYS[tier]
            if max_days is None:
                continue

            expiration_cap = link.created_at + timedelta(days=max_days)
            if link.expires_at is None or link.expires_at > expiration_cap:
                link.expires_at = expiration_cap
                updated_links += 1

        db.commit()
        return updated_links
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Capped expiration for {migrate()} existing links.")
