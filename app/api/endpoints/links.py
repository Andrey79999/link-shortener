from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.link_schema import LinkCreate, LinkResponse
from models.link import Link
from db.session import get_db
from services.link_service import generate_short_code
from tasks.process import process_statistics

router= APIRouter()

@router.post("/", response_model=LinkResponse)
def create_link(link: LinkCreate, db: Session = Depends(get_db)):
    short_code = generate_short_code(str(link.original_url))
    db_link = db.query(Link).filter(Link.short_code == short_code).first()
    if not db_link:
        db_link = Link(original_url=str(link.original_url), short_code=short_code)
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

