from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Resource
from app.schemas import ResourceIn, ResourceOut

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("", response_model=ResourceOut, status_code=201)
def create_resource(body: ResourceIn, db: Session = Depends(get_db)):
    if db.scalar(select(Resource).where(Resource.name == body.name)):
        raise HTTPException(409, "A resource with this name already exists")
    resource = Resource(name=body.name)
    db.add(resource)
    db.commit()
    return resource


@router.get("", response_model=list[ResourceOut])
def list_resources(db: Session = Depends(get_db)):
    return db.scalars(select(Resource).order_by(Resource.id)).all()
