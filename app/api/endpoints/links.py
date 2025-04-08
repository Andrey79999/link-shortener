from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from services.auth_service import get_current_user
from schemas.link_schema import LinkCreate, LinkResponse, LinkDelete, LinkCreateCustom, LinkUpdateCustom
from models.link import Link, LinkStats
from models.user import User
from db.session import get_db
from services.link_service import generate_short_code, get_geo_info
from tasks.process import process_statistics

router= APIRouter()


@router.post("/", response_model=LinkResponse)
def create_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    short_code = generate_short_code()
    db_link = db.query(Link).filter(Link.original_url == str(link.original_url), Link.user_id == current_user.id).first()
    if not db_link:
        db_link = Link(
            user_id=current_user.id,
            original_url=str(link.original_url),
            short_code=short_code
        )
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
    return db_link


@router.post("/create-custom-link", response_model=LinkResponse)
def create_custom_link(
    link: LinkCreateCustom,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if db.query(Link).filter(Link.short_code == link.custom_code).first():
        raise HTTPException(status_code=400, detail="Custom code already exists")
    
    db_link = db.query(Link).filter(Link.original_url == str(link.original_url), Link.user_id == current_user.id).first()
    if not db_link:
        db_link = Link(
            user_id=current_user.id,
            original_url=str(link.original_url),
            short_code=link.custom_code
        )
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
    else:
        db.query(Link).filter(Link.id == db_link.id).update({"short_code": link.custom_code})
        db.commit()
        db.refresh(db_link)
    return db_link


@router.get("/{short_code}", response_model=LinkResponse)
def redirect_link(short_code: str, request: Request, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    db_link.clicks += 1
    country, city = get_geo_info(request.client.host)
    stats = LinkStats(
        link_id = db_link.id,
        ip = request.client.host,
        user_agent = request.headers.get("User-Agent"),
        country = country,
        city = city
    )
    db.add(stats)
    db.commit()
    return db_link


@router.post("/my-links", response_model=List[LinkResponse])
def get_user_links(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.user_id == current_user.id).all()
    return db_link


@router.post("/delete-links", response_model=bool)
def delete_links(
    delete_links: List[LinkDelete],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ids = [link.id for link in delete_links]
    query = db.query(Link).filter(Link.id.in_(ids), Link.user_id == current_user.id)
    if query.count() != len(ids):
        raise HTTPException(status_code=404, detail="Some links not found")
    query.delete(synchronize_session=False)
    db.commit()
    return True


@router.put("/update-link", response_model=LinkResponse)
def update_link(
    updated_data: LinkUpdateCustom,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_link = db.query(Link).filter(Link.id == updated_data.link_id, Link.user_id == current_user.id).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")

    if updated_data.custom_code and db.query(Link).filter(Link.short_code == updated_data.custom_code).first():
        raise HTTPException(status_code=400, detail="Custom code already exists")

    db_link.original_url = str(updated_data.original_url)
    db_link.short_code = updated_data.custom_code

    db.commit()
    db.refresh(db_link)
    return db_link
