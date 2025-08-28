from __future__ import annotations
from datetime import date as date_cls, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_session
from .. import models, schemas
from ..external import fetch_motivational_quote

router = APIRouter(prefix="/habits", tags=["habits"])

@router.post("", response_model=schemas.HabitRead, status_code=status.HTTP_201_CREATED)
async def create_habit(payload: schemas.HabitCreate, db: Session = Depends(get_session)):
    # enforce simple uniqueness by name
    exists = db.scalar(select(func.count()).select_from(models.Habit).where(models.Habit.name == payload.name))
    if exists:
        raise HTTPException(status_code=409, detail="Habit with this name already exists.")
    habit = models.Habit(name=payload.name, description=payload.description)
    db.add(habit)
    db.commit()
    db.refresh(habit)

    quote = await fetch_motivational_quote()
    # attach transient field; not stored in DB
    data = schemas.HabitRead.model_validate(habit)
    data.motivational_quote = quote
    return data

@router.get("", response_model=list[schemas.HabitRead])
def list_habits(db: Session = Depends(get_session)):
    habits = db.scalars(select(models.Habit).order_by(models.Habit.id)).all()
    return [schemas.HabitRead.model_validate(h) for h in habits]

@router.get("/{habit_id}", response_model=schemas.HabitRead)
def get_habit(habit_id: int, db: Session = Depends(get_session)):
    habit = db.get(models.Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return schemas.HabitRead.model_validate(habit)

@router.post("/{habit_id}/logs", response_model=schemas.HabitLogRead, status_code=201)
def add_log(habit_id: int, payload: schemas.HabitLogCreate, db: Session = Depends(get_session)):
    habit = db.get(models.Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log_date = payload.log_date or date_cls.today()
    log = models.HabitLog(habit_id=habit_id, log_date=log_date)
    db.add(log)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Log for this date already exists")
    db.refresh(log)
    return schemas.HabitLogRead.model_validate(log)

@router.get("/{habit_id}/stats", response_model=schemas.HabitStats)
def get_stats(habit_id: int, db: Session = Depends(get_session)):
    habit = db.get(models.Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    logs = db.scalars(
        select(models.HabitLog).where(models.HabitLog.habit_id == habit_id).order_by(models.HabitLog.log_date.asc())
    ).all()
    total = len(logs)
    if total == 0:
        return schemas.HabitStats(total_days=0, streak_current=0, streak_longest=0)

    # compute longest streak
    longest = 1
    streak = 1
    for i in range(1, total):
        if logs[i].log_date == logs[i-1].log_date + timedelta(days=1):
            streak += 1
        else:
            longest = max(longest, streak)
            streak = 1
    longest = max(longest, streak)

    # compute current streak (ending at last logged day)
    current = 1
    for i in range(total-1, 0, -1):
        if logs[i].log_date == logs[i-1].log_date + timedelta(days=1):
            current += 1
        else:
            break

    return schemas.HabitStats(total_days=total, streak_current=current, streak_longest=longest)