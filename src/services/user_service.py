from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate
from typing import List, Optional


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_create: UserCreate) -> UserRead:
        user = User(**user_create.dict())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserRead.from_orm(user)

    def get_user(self, user_id: int) -> Optional[UserRead]:
        user = self.db.query(User).filter(User.id == user_id).first()
        return UserRead.from_orm(user) if user else None

    def get_all_users(self) -> List[UserRead]:
        users = self.db.query(User).all()
        return [UserRead.from_orm(user) for user in users]

    def update_user(self, user_id: int, user_update: UserCreate) -> Optional[UserRead]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in user_update.dict().items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
            return UserRead.from_orm(user)
        return None

    def delete_user(self, user_id: int) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
