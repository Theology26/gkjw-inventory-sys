from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentikasi login untuk pengurus POKJA, Super Admin, dan Majelis.
    Menerima username (e.g. admin_sukun) atau email.
    """
    identifier = (payload.identifier or payload.username or payload.email or "").strip()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama pengguna (username) atau email wajib diisi."
        )

    user = db.query(User).filter(
        (User.username.ilike(identifier)) | (User.email.ilike(identifier))
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nama pengguna atau kata sandi tidak valid."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun ini telah dinonaktifkan."
        )

    token = create_access_token(
        subject=user.id,
        claims={
            "role": user.role.value,
            "email": user.email,
            "username": user.username,
            "pokja_id": user.pokja_id
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        role=user.role,
        pokja_id=user.pokja_id
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Mengambil data profil pengguna yang sedang login."""
    return current_user

