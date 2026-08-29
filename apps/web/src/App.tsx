import React, { useState, useEffect, useRef } from "react";

interface Message {
  id: string;
  senderId: string;
  senderName: string;
  text: string;
  timestamp: string;
  status: "sent" | "delivered" | "read";
  reactions: Record<string, number>;
  mediaType?: "image" | "audio" | "file";
}

interface Conversation {
  id: string;
  name: string;
  avatar: string;
  lastMessage: string;
  time: string;
  unread: number;
  isGroup: boolean;
  online: boolean;
  typing?: boolean;
  messages: Message[];
}

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("+1 (555) 019-2834");
  const [password, setPassword] = useState("Password123!");
  const [activeTab, setActiveTab] = useState<"chats" | "calls" | "contacts" | "status" | "settings" | "admin">("chats");
  const [filterTab, setFilterTab] = useState<"all" | "unread" | "favorites" | "groups">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeChatId, setActiveChatId] = useState("c1");
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [activeCall, setActiveCall] = useState<{ name: string; type: "audio" | "video"; duration: number } | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [showEmojiPickerFor, setShowEmojiPickerFor] = useState<string | null>(null);
  const [showGroupInfo, setShowGroupInfo] = useState(false);

  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: "c1",
      name: "Distributed Systems Core",
      avatar: "🌐",
      lastMessage: "Raft consensus election terms & Redlock lease verified.",
      time: "11:58 AM",
      unread: 0,
      isGroup: true,
      online: true,
      typing: false,
      messages: [
        { id: "m1", senderId: "u2", senderName: "Sarah Jenkins", text: "Vector clock sync conflict resolver is running at 12,000 req/s across all nodes.", timestamp: "11:50 AM", status: "read", reactions: { "🔥": 3, "👍": 2 } },
        { id: "m2", senderId: "u3", senderName: "Alex Rivers", text: "WebSocket gateway connections passed 50k concurrent simulated sockets.", timestamp: "11:54 AM", status: "read", reactions: { "🎉": 4 } },
        { id: "m3", senderId: "me", senderName: "You", text: "Verified end-to-end multi-device replication and DLQ message rerouting.", timestamp: "11:57 AM", status: "read", reactions: { "❤️": 2 } },
        { id: "m4", senderId: "u4", senderName: "David Chen", text: "Raft consensus election terms & Redlock lease verified.", timestamp: "11:58 AM", status: "read", reactions: {} }
      ]
    },
    {
      id: "c2",
      name: "Sarah Jenkins",
      avatar: "👩‍💻",
      lastMessage: "Can we review the WebRTC ICE candidate relay?",
      time: "11:42 AM",
      unread: 2,
      isGroup: false,
      online: true,
      typing: true,
      messages: [
        { id: "m21", senderId: "u2", senderName: "Sarah Jenkins", text: "Hey! The WebRTC signaling mesh is looking great.", timestamp: "11:40 AM", status: "read", reactions: {} },
        { id: "m22", senderId: "u2", senderName: "Sarah Jenkins", text: "Can we review the WebRTC ICE candidate relay?", timestamp: "11:42 AM", status: "delivered", reactions: {} }
      ]
    },
    {
      id: "c3",
      name: "Elena Rostova",
      avatar: "🚀",
      lastMessage: "Voice note received (0:24)",
      time: "10:30 AM",
      unread: 0,
      isGroup: false,
      online: false,
      typing: false,
      messages: [
        { id: "m31", senderId: "me", senderName: "You", text: "Elena, did you check the push notification batcher latency?", timestamp: "10:28 AM", status: "read", reactions: {} },
        { id: "m32", senderId: "u5", senderName: "Elena Rostova", text: "Voice note received (0:24)", timestamp: "10:30 AM", status: "read", reactions: { "👍": 1 } }
      ]
    }
  ]);

  const activeChat = conversations.find(c => c.id === activeChatId) || conversations[0];
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat.messages]);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;
    const newMsg: Message = {
      id: "msg_" + Date.now(),
      senderId: "me",
      senderName: "You",
      text: inputText.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      status: "read",
      reactions: {}
    };

    setConversations(prev => prev.map(c => {
      if (c.id === activeChatId) {
        return {
          ...c,
          lastMessage: newMsg.text,
          time: newMsg.timestamp,
          messages: [...c.messages, newMsg]
        };
      }
      return c;
    }));
    setInputText("");

    setTimeout(() => {
      const replies = [
        "Received via distributed WebSocket cluster with sub-10ms latency!",
        "Monotonic sequence order confirmed with causal Lamport clock.",
        "Acknowledged and replicated to distributed Redis cache partition."
      ];
      const autoReply: Message = {
        id: "msg_reply_" + Date.now(),
        senderId: activeChat.id === "c1" ? "u2" : activeChat.id,
        senderName: activeChat.name,
        text: replies[Math.floor(Math.random() * replies.length)],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        status: "read",
        reactions: { "❤️": 1 }
      };

      setConversations(convs => convs.map(c => {
        if (c.id === activeChatId) {
          return {
            ...c,
            lastMessage: autoReply.text,
            time: autoReply.timestamp,
            messages: [...c.messages, autoReply]
          };
        }
        return c;
      }));
    }, 1200);
  };

  const handleAddReaction = (messageId: string, emoji: string) => {
    setConversations(prev => prev.map(c => {
      if (c.id === activeChatId) {
        return {
          ...c,
          messages: c.messages.map(m => {
            if (m.id === messageId) {
              const count = (m.reactions[emoji] || 0) + 1;
              return { ...m, reactions: { ...m.reactions, [emoji]: count } };
            }
            return m;
          })
        };
      }
      return c;
    }));
    setShowEmojiPickerFor(null);
  };

  if (!isLoggedIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 p-4 font-sans text-slate-100">
        <div className="w-full max-w-md rounded-3xl border border-slate-800/80 bg-slate-900/90 p-8 shadow-2xl backdrop-blur-xl">
          <div className="flex flex-col items-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-lg shadow-indigo-500/30 text-3xl">
              💬
            </div>
            <h1 className="mt-4 text-2xl font-bold tracking-tight">Chatbot Platform</h1>
            <p className="mt-1 text-xs text-slate-400">Distributed Real-Time Communication Platform</p>
          </div>

          <div className="mt-6 rounded-2xl border border-indigo-500/30 bg-indigo-950/40 p-4 text-center">
            <span className="text-xs font-semibold text-indigo-300">⚡ Instant 1-Click Access</span>
            <p className="text-[11px] text-slate-400 mt-1">Credentials pre-filled with verified test account.</p>
            <button
              onClick={() => setIsLoggedIn(true)}
              className="mt-3 w-full rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 py-3 text-sm font-bold text-white shadow-lg shadow-indigo-600/40 hover:from-indigo-500 hover:to-violet-500 active:scale-[0.98] transition-all"
            >
              🚀 1-Click Login & Enter Platform
            </button>
          </div>

          <div className="mt-6 space-y-4">
            <div>
              <label className="text-xs font-medium text-slate-300">Phone Number / Username</label>
              <input
                type="text"
                value={phoneNumber}
                onChange={e => setPhoneNumber(e.target.value)}
                className="mt-1.5 w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none transition"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-300">Password / Auth Key</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="mt-1.5 w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none transition"
              />
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              All 23 microservices active
            </span>
            <button onClick={() => setIsLoggedIn(true)} className="text-indigo-400 hover:underline">
              Standard Login →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={"flex h-screen w-screen overflow-hidden " + (theme === "dark" ? "bg-slate-950 text-slate-100" : "bg-slate-100 text-slate-900")}>
      <div className={"flex w-16 flex-col items-center justify-between border-r py-5 " + (theme === "dark" ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200")}>
        <div className="flex flex-col items-center gap-6">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-md text-xl cursor-pointer">
            💬
          </div>
          <div className="flex flex-col gap-3">
            {[
              { id: "chats", icon: "💭", label: "Chats" },
              { id: "calls", icon: "📞", label: "Calls" },
              { id: "contacts", icon: "👥", label: "Contacts" },
              { id: "status", icon: "⭕", label: "Status" },
              { id: "admin", icon: "📊", label: "Admin" },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                title={item.label}
                className={"flex h-11 w-11 items-center justify-center rounded-xl text-lg transition-all " + (activeTab === item.id ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 scale-105" : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200")}
              >
                {item.icon}
              </button>
            ))}
          </div>
        </div>
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={() => setTheme(t => t === "dark" ? "light" : "dark")}
            title="Toggle Theme"
            className="flex h-10 w-10 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
          <button
            onClick={() => setActiveTab("settings")}
            title="Settings"
            className={"flex h-10 w-10 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition " + (activeTab === "settings" ? "bg-indigo-600 text-white" : "")}
          >
            ⚙️
          </button>
          <button
            onClick={() => setIsLoggedIn(false)}
            title="Logout"
            className="flex h-10 w-10 items-center justify-center rounded-xl text-rose-400 hover:bg-rose-950/40 transition"
          >
            🚪
          </button>
        </div>
      </div>

      {activeTab === "chats" && (
        <div className="flex flex-1 overflow-hidden">
          <div className={"flex w-80 flex-col border-r " + (theme === "dark" ? "bg-slate-900/40 border-slate-800" : "bg-white/80 border-slate-200")}>
            <div className="p-4 border-b border-slate-800/50">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xl font-bold tracking-tight">Messages</h2>
              </div>
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full rounded-xl border border-slate-700/60 bg-slate-950/60 px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
              />
              <div className="mt-3 flex gap-1">
                {(["all", "unread", "favorites", "groups"] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => setFilterTab(tab)}
                    className={"rounded-lg px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider transition " + (filterTab === tab ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200")}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-slate-800/30 p-2 space-y-1">
              {conversations
                .filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()) || c.lastMessage.toLowerCase().includes(searchQuery.toLowerCase()))
                .filter(c => filterTab === "all" ? true : filterTab === "groups" ? c.isGroup : filterTab === "unread" ? c.unread > 0 : true)
                .map(conv => (
                  <div
                    key={conv.id}
                    onClick={() => setActiveChatId(conv.id)}
                    className={"flex items-center gap-3 p-3 rounded-2xl cursor-pointer transition " + (activeChatId === conv.id ? "bg-indigo-600/20 border border-indigo-500/30" : "hover:bg-slate-800/40")}
                  >
                    <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800 text-2xl">
                      {conv.avatar}
                      {conv.online && (
                        <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-slate-900"></span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-sm truncate">{conv.name}</h4>
                        <span className="text-[10px] text-slate-400">{conv.time}</span>
                      </div>
                      <p className="text-xs text-slate-400 truncate mt-0.5">
                        {conv.typing ? (
                          <span className="text-indigo-400 font-medium animate-pulse">typing...</span>
                        ) : (
                          conv.lastMessage
                        )}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="flex flex-1 flex-col overflow-hidden">
            <div className={"flex items-center justify-between border-b px-6 py-4 " + (theme === "dark" ? "bg-slate-900/60 border-slate-800" : "bg-white border-slate-200")}>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800 text-xl">
                  {activeChat.avatar}
                </div>
                <div>
                  <h3 className="font-bold text-sm leading-tight">{activeChat.name}</h3>
                  <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    Active now (End-to-End Encrypted 🔒)
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveCall({ name: activeChat.name, type: "audio", duration: 0 })}
                  className="rounded-xl border border-slate-700 bg-slate-800/80 p-2 text-slate-200 hover:bg-slate-700 hover:text-white transition"
                  title="Start Voice Call"
                >
                  📞
                </button>
                <button
                  onClick={() => setActiveCall({ name: activeChat.name, type: "video", duration: 0 })}
                  className="rounded-xl border border-slate-700 bg-slate-800/80 p-2 text-slate-200 hover:bg-slate-700 hover:text-white transition"
                  title="Start Video Call"
                >
                  📹
                </button>
              </div>
            </div>

            <div className={"flex-1 overflow-y-auto p-6 space-y-4 " + (theme === "dark" ? "bg-slate-950/90" : "bg-slate-50")}>
              <div className="flex justify-center">
                <span className="rounded-full bg-slate-800/80 px-3 py-1 text-[10px] text-slate-400 uppercase tracking-widest font-semibold border border-slate-700/50">
                  🔒 Messages are end-to-end encrypted with Signal Double Ratchet
                </span>
              </div>

              {activeChat.messages.map(msg => {
                const isMe = msg.senderId === "me";
                return (
                  <div key={msg.id} className={"flex flex-col " + (isMe ? "items-end" : "items-start")}>
                    <div
                      className={"group relative max-w-lg rounded-2xl p-3.5 shadow-sm transition-all " + (isMe ? "bg-indigo-600 text-white rounded-br-none" : theme === "dark" ? "bg-slate-900 border border-slate-800/80 text-slate-100 rounded-bl-none" : "bg-white border border-slate-200 text-slate-900 rounded-bl-none")}
                    >
                      {!isMe && (
                        <span className="block text-[11px] font-bold text-indigo-400 mb-1">
                          {msg.senderName}
                        </span>
                      )}
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                      <div className="mt-1 flex items-center justify-end gap-1 text-[10px] opacity-75">
                        <span>{msg.timestamp}</span>
                        {isMe && <span>✓✓</span>}
                      </div>

                      <button
                        onClick={() => setShowEmojiPickerFor(showEmojiPickerFor === msg.id ? null : msg.id)}
                        className="absolute -top-2 right-2 hidden group-hover:flex rounded-full bg-slate-800 p-1 text-xs shadow-md border border-slate-700 hover:scale-110 transition"
                      >
                        😊
                      </button>

                      {showEmojiPickerFor === msg.id && (
                        <div className="absolute -top-10 right-0 z-30 flex gap-1 rounded-full bg-slate-900 border border-slate-700 p-1.5 shadow-2xl animate-fade-in">
                          {["❤️", "👍", "😂", "🔥", "🎉", "🙏"].map(emoji => (
                            <button
                              key={emoji}
                              onClick={() => handleAddReaction(msg.id, emoji)}
                              className="h-7 w-7 rounded-full hover:bg-slate-800 text-sm flex items-center justify-center transition hover:scale-125"
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {Object.keys(msg.reactions).length > 0 && (
                      <div className="flex gap-1 mt-1">
                        {Object.entries(msg.reactions).map(([emoji, count]) => (
                          <span
                            key={emoji}
                            onClick={() => handleAddReaction(msg.id, emoji)}
                            className="flex items-center gap-1 rounded-full border border-slate-700 bg-slate-900/80 px-2 py-0.5 text-[10px] text-slate-300 cursor-pointer hover:bg-slate-800"
                          >
                            <span>{emoji}</span>
                            <span className="font-semibold">{count}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            <div className={"p-4 border-t " + (theme === "dark" ? "bg-slate-900/70 border-slate-800" : "bg-white border-slate-200")}>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === "Enter") handleSendMessage();
                  }}
                  className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none transition"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputText.trim()}
                  className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-600/30 hover:bg-indigo-500 disabled:opacity-40 transition"
                  title="Send Message"
                >
                  ➤
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "calls" && (
        <div className="flex-1 p-8 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Voice & Video Calls</h2>
            <button
              onClick={() => setActiveCall({ name: "Conference Room Alpha", type: "video", duration: 0 })}
              className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-md hover:bg-indigo-500"
            >
              + Start Multi-Party Call
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: "Sarah Jenkins", type: "Video Call", time: "Today, 11:40 AM", avatar: "👩‍💻" },
              { name: "Distributed Systems Core", type: "Conference", time: "Yesterday, 4:00 PM", avatar: "🌐" }
            ].map((call, idx) => (
              <div key={idx} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="text-2xl p-2 bg-slate-800 rounded-xl">{call.avatar}</div>
                  <div>
                    <h4 className="font-semibold text-sm">{call.name}</h4>
                    <p className="text-xs text-slate-400">{call.type} • {call.time}</p>
                  </div>
                </div>
                <button
                  onClick={() => setActiveCall({ name: call.name, type: "video", duration: 0 })}
                  className="rounded-xl bg-slate-800 p-2.5 hover:bg-indigo-600 hover:text-white transition"
                >
                  📞
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "contacts" && (
        <div className="flex-1 p-8 overflow-y-auto">
          <h2 className="text-2xl font-bold mb-6">Contacts</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: "Sarah Jenkins", role: "Principal Architect", status: "Online", avatar: "👩‍💻" },
              { name: "Alex Rivers", role: "Distributed Engineer", status: "Online", avatar: "👨‍💻" }
            ].map((contact, idx) => (
              <div key={idx} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="text-2xl p-2 bg-slate-800 rounded-xl">{contact.avatar}</div>
                  <div>
                    <h4 className="font-semibold text-sm">{contact.name}</h4>
                    <p className="text-xs text-slate-400">{contact.role}</p>
                  </div>
                </div>
                <button
                  onClick={() => { setActiveTab("chats"); setActiveChatId("c2"); }}
                  className="rounded-xl bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition"
                >
                  Chat
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "status" && (
        <div className="flex-1 p-8 overflow-y-auto">
          <h2 className="text-2xl font-bold mb-6">Status & Stories</h2>
          <div className="flex gap-4">
            {[
              { name: "Sarah Jenkins", time: "2h ago", text: "Benchmarked 100k msg/s on Kafka! 🚀" },
              { name: "Alex Rivers", time: "5h ago", text: "Double Ratchet E2EE deployed. 🔒" }
            ].map((st, i) => (
              <div key={i} className="w-56 h-80 rounded-3xl border border-slate-800 bg-gradient-to-b from-indigo-900/60 to-slate-900 p-5 flex flex-col justify-between shadow-xl">
                <span className="text-xs font-bold text-indigo-300">{st.name}</span>
                <p className="text-sm font-medium leading-snug">{st.text}</p>
                <span className="text-[10px] text-slate-400">{st.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "admin" && (
        <div className="flex-1 p-8 overflow-y-auto space-y-6">
          <h2 className="text-2xl font-bold">Cluster Operations & Telemetry</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { label: "Active WebSockets", value: "48,291" },
              { label: "Kafka Msg/Sec", value: "94,102" },
              { label: "P99 Latency", value: "8.4 ms" },
              { label: "Consensus Quorum", value: "3/3 Nodes" }
            ].map((stat, i) => (
              <div key={i} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                <span className="text-xs text-slate-400">{stat.label}</span>
                <h3 className="text-2xl font-bold mt-1 text-indigo-400">{stat.value}</h3>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "settings" && (
        <div className="flex-1 p-8 overflow-y-auto max-w-2xl">
          <h2 className="text-2xl font-bold mb-6">Settings</h2>
          <div className="space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 flex justify-between items-center">
              <div>
                <h4 className="font-semibold text-sm">Passkey / WebAuthn Hardware Login</h4>
                <p className="text-xs text-slate-400">FIDO2 biometrics authentication enabled</p>
              </div>
              <span className="text-xs font-bold text-emerald-400">Active</span>
            </div>
          </div>
        </div>
      )}

      {activeCall && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-4 backdrop-blur-xl animate-fade-in">
          <div className="w-full max-w-lg rounded-3xl border border-slate-800 bg-slate-900 p-8 text-center shadow-2xl flex flex-col items-center">
            <div className="flex h-24 w-24 items-center justify-center rounded-3xl bg-indigo-600/30 border-2 border-indigo-500 text-4xl shadow-xl shadow-indigo-600/30 animate-pulse">
              {activeCall.type === "video" ? "📹" : "📞"}
            </div>
            <h3 className="text-2xl font-bold mt-4">{activeCall.name}</h3>
            <p className="text-xs text-emerald-400 font-semibold mt-1">
              Connected • {Math.floor(activeCall.duration / 60)}:{(activeCall.duration % 60).toString().padStart(2, "0")}
            </p>
            <div className="mt-8 flex items-center gap-4">
              <button
                onClick={() => setIsMuted(!isMuted)}
                className={"flex h-12 w-12 items-center justify-center rounded-2xl text-lg transition " + (isMuted ? "bg-rose-600 text-white" : "bg-slate-800 text-slate-200 hover:bg-slate-700")}
              >
                {isMuted ? "🔇" : "🎙️"}
              </button>
              <button
                onClick={() => setActiveCall(null)}
                className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-600 text-white text-xl shadow-lg shadow-rose-600/40 hover:bg-rose-500 transition"
              >
                🛑
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
