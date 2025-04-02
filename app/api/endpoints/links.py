from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from services.auth_service import get_current_user
from schemas.link_schema import LinkCreate, LinkResponse
from models.link import Link
from models.user import User
from db.session import get_db
from services.link_service import generate_short_code
from tasks.process import process_statistics

router= APIRouter()


@router.post("/", response_model=LinkResponse)
def create_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
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


@router.get("/{short_code}", response_model=LinkResponse)
def redirect_link(short_code: str, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    db_link.clicks += 1
    db.commit()
    # TODO
    # process_statistics.delay(db_link.id)
    return db_link


@router.get("/{user_id}/links", response_model=List[LinkResponse])
def get_user_links(user_id: int, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.user_id == user_id).all()
    return db_link
