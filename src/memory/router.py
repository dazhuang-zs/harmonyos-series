from fastapi import APIRouter, HTTPException

from src.memory.schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
)
from src.memory.store import store

router = APIRouter(prefix="/api/v1/conversations", tags=["对话管理"])


@router.post("/", response_model=ConversationResponse)
async def create_conversation(req: ConversationCreateRequest):
    """创建新对话"""
    conv = store.create(req.title)
    return ConversationResponse(
        conversation_id=conv.conversation_id,
        title=conv.title,
        message_count=0,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations():
    """获取所有对话列表"""
    conversations = store.list_all()
    return [
        ConversationResponse(
            conversation_id=c.conversation_id,
            title=c.title,
            message_count=len(c.messages),
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str):
    """获取对话详情"""
    conv = store.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    return ConversationDetailResponse(
        conversation_id=conv.conversation_id,
        title=conv.title,
        messages=[
            MessageResponse(
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
            )
            for m in conv.messages
        ],
        user_preferences=conv.user_preferences,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    if not store.delete(conversation_id):
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"status": "deleted"}
