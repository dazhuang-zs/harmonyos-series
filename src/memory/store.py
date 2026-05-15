"""对话历史存储：内存实现（可扩展为 Redis/DB）"""

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # user / assistant / system
    content: str
    timestamp: float = field(default_factory=time.time)
    token_count: int = 0


@dataclass
class Conversation:
    conversation_id: str
    title: str = "新对话"
    messages: list[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    user_preferences: dict = field(default_factory=dict)


class ConversationStore:
    """对话存储（内存实现）"""

    def __init__(self):
        self._conversations: dict[str, Conversation] = {}

    def create(self, title: str = "新对话") -> Conversation:
        conv_id = uuid.uuid4().hex[:12]
        conv = Conversation(conversation_id=conv_id, title=title)
        self._conversations[conv_id] = conv
        return conv

    def get(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def list_all(self) -> list[Conversation]:
        return sorted(
            self._conversations.values(),
            key=lambda c: c.updated_at,
            reverse=True,
        )

    def delete(self, conversation_id: str) -> bool:
        return self._conversations.pop(conversation_id, None) is not None

    def add_message(self, conversation_id: str, role: str, content: str, token_count: int = 0) -> Message | None:
        conv = self.get(conversation_id)
        if not conv:
            return None
        msg = Message(role=role, content=content, token_count=token_count)
        conv.messages.append(msg)
        conv.updated_at = time.time()
        return msg

    def get_messages(self, conversation_id: str) -> list[Message]:
        conv = self.get(conversation_id)
        return conv.messages if conv else []

    def update_title(self, conversation_id: str, title: str) -> bool:
        conv = self.get(conversation_id)
        if conv:
            conv.title = title
            return True
        return False

    def update_preferences(self, conversation_id: str, preferences: dict) -> bool:
        conv = self.get(conversation_id)
        if conv:
            conv.user_preferences.update(preferences)
            return True
        return False


# 全局单例
store = ConversationStore()
