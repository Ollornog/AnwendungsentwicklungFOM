"""CRUD fuer Benutzer.

Rudimentaer fuer die Demo: der eingeloggte Admin kann weitere Nutzer
anlegen, Passwoerter aendern und User loeschen. Der 'admin'-Account ist
geschuetzt und kann weder bearbeitet noch geloescht werden.
"""
# `from __future__ import annotations` absichtlich NICHT: sonst wird
# aus `-> None` ein String, den FastAPI zu `type(None)` aufloest. Die
# Klasse NoneType ist truthy, wodurch FastAPI 0.115 bei Status 204 die
# Assertion "Status code 204 must not have a response body" wirft und
# der Service beim Start crasht.

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_admin
from app.models import User
from app.schemas import UserCreate, UserList, UserListItem, UserUpdate
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

# Account-Namen, die nicht veraendert werden duerfen. Schuetzt den
# bootstrap-Admin davor, sich per UI selbst aus dem System zu sperren.
PROTECTED_USERNAMES = {"admin"}


def _get_user_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden")
    return user


def _assert_not_protected(user: User) -> None:
    if user.username in PROTECTED_USERNAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account '{user.username}' ist geschuetzt und kann nicht veraendert werden",
        )


@router.get("", response_model=UserList)
def list_users(
    current_user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> UserList:
    rows = db.scalars(select(User).order_by(User.username)).all()
    return UserList(items=[UserListItem.model_validate(u) for u in rows])


@router.post("", response_model=UserListItem, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> UserListItem:
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Benutzername existiert bereits"
        )
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserListItem.model_validate(user)


@router.put("/{user_id}", response_model=UserListItem)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> UserListItem:
    user = _get_user_or_404(db, user_id)
    _assert_not_protected(user)
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.role is not None:
        user.role = payload.role
    db.commit()
    db.refresh(user)
    return UserListItem.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    user = _get_user_or_404(db, user_id)
    _assert_not_protected(user)
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Eigenen Account nicht loeschen",
        )
    db.delete(user)
    db.commit()
