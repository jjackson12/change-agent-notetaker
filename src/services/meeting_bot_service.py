from sqlalchemy.orm import Session
from models.meeting_bot import MeetingBot
from schemas.meeting_bot import MeetingBotCreate, MeetingBotUpdate

class MeetingBotService:
    def __init__(self, db: Session):
        self.db = db

    def create_meeting_bot(self, meeting_bot: MeetingBotCreate) -> MeetingBot:
        db_meeting_bot = MeetingBot(**meeting_bot.dict())
        self.db.add(db_meeting_bot)
        self.db.commit()
        self.db.refresh(db_meeting_bot)
        return db_meeting_bot

    def get_meeting_bot(self, bot_id: int) -> MeetingBot:
        return self.db.query(MeetingBot).filter(MeetingBot.id == bot_id).first()

    def update_meeting_bot(self, bot_id: int, meeting_bot: MeetingBotUpdate) -> MeetingBot:
        db_meeting_bot = self.get_meeting_bot(bot_id)
        if db_meeting_bot:
            for key, value in meeting_bot.dict(exclude_unset=True).items():
                setattr(db_meeting_bot, key, value)
            self.db.commit()
            self.db.refresh(db_meeting_bot)
        return db_meeting_bot

    def delete_meeting_bot(self, bot_id: int) -> bool:
        db_meeting_bot = self.get_meeting_bot(bot_id)
        if db_meeting_bot:
            self.db.delete(db_meeting_bot)
            self.db.commit()
            return True
        return False

    def list_meeting_bots(self):
        return self.db.query(MeetingBot).all()