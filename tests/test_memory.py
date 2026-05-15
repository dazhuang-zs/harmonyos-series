import pytest

from src.memory.store import ConversationStore


class TestConversationStore:
    def test_create_conversation(self):
        store = ConversationStore()
        conv = store.create("测试对话")
        assert conv.title == "测试对话"
        assert conv.conversation_id
        assert len(conv.messages) == 0

    def test_get_conversation(self):
        store = ConversationStore()
        conv = store.create()
        retrieved = store.get(conv.conversation_id)
        assert retrieved is not None
        assert retrieved.conversation_id == conv.conversation_id

    def test_get_nonexistent(self):
        store = ConversationStore()
        assert store.get("nonexistent") is None

    def test_add_message(self):
        store = ConversationStore()
        conv = store.create()
        msg = store.add_message(conv.conversation_id, "user", "你好")
        assert msg is not None
        assert msg.role == "user"
        assert msg.content == "你好"

        messages = store.get_messages(conv.conversation_id)
        assert len(messages) == 1

    def test_list_conversations(self):
        store = ConversationStore()
        store.create("对话1")
        store.create("对话2")
        conversations = store.list_all()
        assert len(conversations) == 2

    def test_delete_conversation(self):
        store = ConversationStore()
        conv = store.create()
        assert store.delete(conv.conversation_id) is True
        assert store.get(conv.conversation_id) is None

    def test_delete_nonexistent(self):
        store = ConversationStore()
        assert store.delete("nonexistent") is False

    def test_update_title(self):
        store = ConversationStore()
        conv = store.create("原标题")
        assert store.update_title(conv.conversation_id, "新标题") is True
        assert store.get(conv.conversation_id).title == "新标题"

    def test_update_preferences(self):
        store = ConversationStore()
        conv = store.create()
        store.update_preferences(conv.conversation_id, {"code_style": "strict"})
        updated = store.get(conv.conversation_id)
        assert updated.user_preferences["code_style"] == "strict"
