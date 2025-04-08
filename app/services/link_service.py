import hashlib
from random import randbytes
import geoip2.database
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from models.link import Link, LinkStats
from schemas.link_schema import LinkUpdateCustom, LinkCreate, LinkCreateCustom


def generate_short_code() -> str:
    """
    Generate a short code for a given URL.

    Args:

    Returns:
        str: A 6-character hexadecimal string representing the short code.
    """
    hash_object = hashlib.md5(randbytes(10))
    return hash_object.hexdigest()[:6]

def get_geo_info(ip: str):
    try:
        reader = geoip2.database.Reader('/app/GeoLite2-City.mmdb')
        response = reader.city(ip)
        country = response.country.iso_code
        city = response.city.name
        return country, city
    except Exception as e:
        print(f"get_geo_info: {e}")
        return None, None

def update_link_service(db: Session, user_id: int, updated_data: LinkUpdateCustom):
    db_link = db.query(Link).filter(Link.id == updated_data.link_id, Link.user_id == user_id).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")

    if updated_data.custom_code:
        duplicate = db.query(Link).filter(Link.short_code == updated_data.custom_code, Link.id != updated_data.link_id).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Custom code already exists")

    db_link.original_url = str(updated_data.original_url)
    db_link.short_code = updated_data.custom_code

    db.commit()
    db.refresh(db_link)
    return db_link

def create_link_service(db: Session, user_id: int, link_data: LinkCreate):
    db_link = db.query(Link).filter(Link.original_url == str(link_data.original_url), Link.user_id == user_id).first()
    if not db_link:
        db_link = Link(
            user_id=user_id,
            original_url=str(link_data.original_url),
            short_code=generate_short_code()
        )
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
    return db_link

def create_custom_link_service(db: Session, user_id: int, link_data: LinkCreateCustom):
    if db.query(Link).filter(Link.short_code == link_data.custom_code).first():
        raise HTTPException(status_code=400, detail="Custom code already exists")

    db_link = db.query(Link).filter(Link.original_url == str(link_data.original_url), Link.user_id == user_id).first()
    if not db_link:
        db_link = Link(
            user_id=user_id,
            original_url=str(link_data.original_url),
            short_code=link_data.custom_code
        )
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
    else:
        db.query(Link).filter(Link.id == db_link.id).update({"short_code": link_data.custom_code})
        db.commit()
        db.refresh(db_link)
    return db_link

def redirect_link_service(db: Session, short_code: str, request: Request):
    db_link = db.query(Link).filter(Link.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")

    db_link.clicks += 1
    country, city = get_geo_info(request.client.host)
    stats = LinkStats(
        link_id=db_link.id,
        ip=request.client.host,
        user_agent=request.headers.get("User-Agent"),
        country=country,
        city=city
    )
    db.add(stats)
    db.commit()
    return db_link

def delete_links_service(db: Session, user_id: int, link_ids: list[int]):
    query = db.query(Link).filter(Link.id.in_(link_ids), Link.user_id == user_id)
    if query.count() != len(link_ids):
        raise HTTPException(status_code=404, detail="Some links not found")
    query.delete(synchronize_session=False)
    db.commit()
    return True
