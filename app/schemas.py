from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, Field

# ---- Habit ----
class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)

class HabitRead(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    motivational_quote: str | None = None  # included on creation

    model_config = {"from_attributes": True}

# ---- Log ----
class HabitLogCreate(BaseModel):
    log_date: date | None = None  # default: today (server side)

class HabitLogRead(BaseModel):
    id: int
    habit_id: int
    log_date: date

    model_config = {"from_attributes": True}

# ---- Stats ----
class HabitStats(BaseModel):
    total_days: int
    streak_current: int
    streak_longest: int