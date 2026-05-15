"use client";

interface Conversation {
  conversation_id: string;
  title: string;
  message_count: number;
  updated_at: number;
}

interface ChatSidebarProps {
  conversations: Conversation[];
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export default function ChatSidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: ChatSidebarProps) {
  return (
    <div className="w-64 flex-shrink-0 border-r border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800">
        <h1 className="text-lg font-bold text-zinc-900 dark:text-white">
          HarmonyOS 助手
        </h1>
        <p className="text-xs text-zinc-500 mt-1">MiMo 大模型驱动</p>
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNew}
        className="mx-3 mt-3 mb-2 px-4 py-2.5 rounded-xl border border-dashed border-zinc-300 dark:border-zinc-700 text-sm text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
      >
        + 新对话
      </button>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
        {conversations.map((conv) => (
          <div
            key={conv.conversation_id}
            onClick={() => onSelect(conv.conversation_id)}
            className={`group flex items-center gap-2 px-3 py-2.5 rounded-xl cursor-pointer transition-colors ${
              conv.conversation_id === activeId
                ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                : "text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
            }`}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{conv.title}</p>
              <p className="text-xs text-zinc-400 mt-0.5">
                {conv.message_count} 条消息
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conv.conversation_id);
              }}
              className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-zinc-400 hover:text-red-500 transition-all"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        ))}

        {conversations.length === 0 && (
          <div className="text-center text-sm text-zinc-400 mt-8">
            暂无对话
          </div>
        )}
      </div>
    </div>
  );
}
