"""Dependencias compartidas: sesión de DB y usuario autenticado."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .security import decode_token
from . import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=True)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión vencida o token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.Usuario).filter_by(username=payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user
