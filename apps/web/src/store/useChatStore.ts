import { create } from 'zustand';
import { Conversation, Message, UserProfile, PresenceStatus } from '../types/chat';

interface ChatState {
  currentUser: UserProfile | null;
  activeConversationId: string | null;
  conversations: Conversation[];
  messages: Record<string, Message[]>; // conversationId -> messages
  activeTypers: Record<string, string[]>; // conversationId -> userIds
  userPresence: Record<string, PresenceStatus>; // userId -> status
  
  setCurrentUser: (user: UserProfile) => void;
  setActiveConversation: (id: string) => void;
  setConversations: (convs: Conversation[]) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateMessageStatus: (messageId: string, status: Message['delivery_state']) => void;
  setTyping: (conversationId: string, userIds: string[]) => void;
  setUserPresence: (userId: string, status: PresenceStatus) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  currentUser: null,
  activeConversationId: null,
  conversations: [],
  messages: {},
  activeTypers: {},
  userPresence: {},

  setCurrentUser: (user) => set({ currentUser: user }),
  setActiveConversation: (id) => set({ activeConversationId: id }),
  setConversations: (convs) => set({ conversations: convs }),
  
  addMessage: (conversationId, message) => set((state) => {
    const existing = state.messages[conversationId] || [];
    if (existing.some((m) => m.id === message.id)) return state;
    return {
      messages: {
        ...state.messages,
        [conversationId]: [...existing, message]
      }
    };
  }),

  updateMessageStatus: (messageId, status) => set((state) => {
    const updatedMessages: Record<string, Message[]> = {};
    for (const [cid, list] of Object.entries(state.messages)) {
      updatedMessages[cid] = list.map((m) => m.id === messageId ? { ...m, delivery_state: status } : m);
    }
    return { messages: updatedMessages };
  }),

  setTyping: (conversationId, userIds) => set((state) => ({
    activeTypers: { ...state.activeTypers, [conversationId]: userIds }
  })),

  setUserPresence: (userId, status) => set((state) => ({
    userPresence: { ...state.userPresence, [userId]: status }
  }))
}));
