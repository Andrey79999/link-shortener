from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from services.auth_service import get_current_user
from schemas.link_schema import LinkCreate, LinkResponse, LinkDelete, LinkCreateCustom, LinkUpdateCustom
from models.link import Link, LinkStats
from models.user import User
from db.session import get_db
from services.link_service import generate_short_code, get_geo_info, update_link_service, create_link_service, create_custom_link_service, redirect_link_service, delete_links_service
from tasks.process import process_statistics

router= APIRouter()


@router.post("/", response_model=LinkResponse)
def create_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_link_service(db, current_user.id, link)


@router.post("/create-custom-link", response_model=LinkResponse)
def create_custom_link(
    link: LinkCreateCustom,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_custom_link_service(db, current_user.id, link)


@router.get("/{short_code}", response_model=LinkResponse)
def redirect_link(short_code: str, request: Request, db: Session = Depends(get_db)):
    return redirect_link_service(db, short_code, request)


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
    link_ids = [link.id for link in delete_links]
    return delete_links_service(db, current_user.id, link_ids)


@router.put("/update-link", response_model=LinkResponse)
def update_link(
    updated_data: LinkUpdateCustom,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_link_service(db, current_user.id, updated_data)
