from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid import UUID
from datetime import datetime, timezone

from back.src.auth.ldap import ldap_auth
from back.src.core.schemas import ItemCreate, ItemRead, ItemUpdate
from back.src.core.models import Item
from back.src.database import get_async_session
from back.src.auth.models import User



router = APIRouter(
    prefix="/todo",
    tags=["ToDoList"]
)

from back.src.main import fastapi_users

current_user = fastapi_users.current_user()

@router.post("/add_item")
async def add_item_to_list(item: ItemCreate, 
                           session: AsyncSession = Depends(get_async_session),
                           user: User = Depends(current_user)):
    item_db = Item(**item.model_dump(), user_id=user.id)
    session.add(item_db)
    await session.commit()

    return {
        "status": "ok",
        "detail": "item added",
        "data": [ItemRead(**item.model_dump(), id=item_db.id, is_done=False)]
    }


@router.get("/get_items")
async def get_items(user: User = Depends(current_user),
                    session: AsyncSession = Depends(get_async_session)):

    query = select(User).options(joinedload(User.to_do_items)).filter(User.id == user.id)
    result = await session.execute(query)
    user_with_items = result.unique().scalars().first()

    res = [ItemRead.model_validate(item, from_attributes=True) for item in user_with_items.to_do_items]

    res.sort(
        key=lambda x: x.do_till if x.do_till is not None else datetime.max.replace(tzinfo=timezone.utc),
    )

    return {
        "status": "ok",
        "detail": "got items",
        "data": res
    }


@router.post("/toggle_status")
async def mark(item_id: UUID, 
               user: User = Depends(current_user),
               session: AsyncSession = Depends(get_async_session)
               ):
    item_db = await session.get(Item, item_id)

    if item_db.user_id != user.id:
        return
    item_db.is_done = not item_db.is_done
    await session.commit()

    return {
        "status": "ok",
        "detail": "item is done",
        "data": [ItemRead(**item_db.__dict__)]
    }


@router.patch("/update_item")
async def update_item(item_id: UUID,
                      new_item: ItemUpdate,
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_user)
                      ):
    item_db = await session.get(Item, item_id)
    if item_db.user_id != user.id:
        return
    to_upd = new_item.model_dump()
    for field, val in to_upd.items():
        if val is not None:
            setattr(item_db, field, val)
    await session.commit()

    return {
        "status": "ok",
        "detail": "item updated",
        "data": [ItemRead(**item_db.__dict__)]
    }


@router.delete("/delete_item")
async def delete_item(item_id,
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_user)
                      ):
    item_db = await session.get(Item, item_id)
    if item_db.user_id != user.id:
        return
    await session.delete(item_db)
    await session.commit()

    return {
        "status": "ok",
        "detail": "item deleted",
        "data": []
    }
