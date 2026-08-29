import React, { useState } from 'react';
import { useChatStore } from '../store/useChatStore';

export const ChatInterface: React.FC = () => {
  const { conversations, activeConversationId, messages, currentUser, setActiveConversation, addMessage } = useChatStore();
  const [inputText, setInputText] = useState('');

  const activeConv = conversations.find((c) => c.id === activeConversationId);
  const activeMessages = activeConversationId ? messages[activeConversationId] || [] : [];

  const handleSendMessage = () => {
    if (!inputText.trim() || !activeConversationId || !currentUser) return;
    const newMsg = {
      id: 'msg-' + Date.now(),
      conversation_id: activeConversationId,
      sender_id: currentUser.id,
      sequence_number: activeMessages.length + 1,
      message_type: 'text' as const,
      content: inputText.trim(),
      delivery_state: 'sent' as const,
      is_edited: false,
      is_deleted_for_everyone: false,
      reactions: {},
      created_at: new Date().toISOString()
    };
    addMessage(activeConversationId, newMsg);
    setInputText('');
  };

  return (
    <div className="flex h-screen w-full bg-slate-900 text-slate-100 antialiased font-sans">
      {/* Sidebar - Conversation List */}
      <div className="w-80 border-r border-slate-800 flex flex-col bg-slate-950">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h1 className="text-xl font-bold tracking-tight text-indigo-400">Chatbot</h1>
          <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" title="Connected" />
        </div>
        <div className="flex-1 overflow-y-auto divide-y divide-slate-800/50">
          {conversations.map((c) => (
            <div
              key={c.id}
              onClick={() => setActiveConversation(c.id)}
              className={`p-3.5 cursor-pointer transition flex items-center gap-3 hover:bg-slate-900 ${
                activeConversationId === c.id ? 'bg-slate-900 border-l-4 border-indigo-500' : ''
              }`}
            >
              <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center font-bold text-slate-300">
                {c.title ? c.title[0].toUpperCase() : 'C'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-baseline">
                  <h3 className="font-semibold text-sm truncate text-slate-200">{c.title || 'Direct Chat'}</h3>
                  {c.unread_count > 0 && (
                    <span className="bg-indigo-600 text-xs px-2 py-0.5 rounded-full font-bold">{c.unread_count}</span>
                  )}
                </div>
                <p className="text-xs text-slate-400 truncate mt-0.5">{c.last_message_preview || 'No messages yet'}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Active Chat Pane */}
      <div className="flex-1 flex flex-col bg-slate-900">
        {activeConv ? (
          <>
            {/* Header */}
            <div className="h-16 border-b border-slate-800 px-6 flex items-center justify-between bg-slate-950/60 backdrop-blur">
              <div>
                <h2 className="font-bold text-slate-100">{activeConv.title || 'Conversation'}</h2>
                <span className="text-xs text-emerald-400 font-medium">● Online</span>
              </div>
            </div>

            {/* Message History */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {activeMessages.map((m) => {
                const isMine = m.sender_id === currentUser?.id;
                return (
                  <div key={m.id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-md px-4 py-2.5 rounded-2xl text-sm shadow-sm ${
                        isMine ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-slate-800 text-slate-200 rounded-bl-none'
                      }`}
                    >
                      <p>{m.content}</p>
                      <div className="flex items-center justify-end gap-1 mt-1 text-[10px] opacity-75">
                        <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        {isMine && <span>✓✓</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Input Bar */}
            <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center gap-3">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type a message..."
                className="flex-1 bg-slate-800/80 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition"
              />
              <button
                onClick={handleSendMessage}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition shadow-md hover:shadow-indigo-500/20"
              >
                Send
              </button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
            <p className="text-base font-medium">Select a conversation to start chatting</p>
          </div>
        )}
      </div>
    </div>
  );
};
