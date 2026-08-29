export type MessageType = 'text' | 'image' | 'video' | 'audio' | 'voice_note' | 'document' | 'location' | 'sticker' | 'gif' | 'system';
export type DeliveryState = 'sending' | 'sent' | 'server_accepted' | 'delivered' | 'read' | 'failed';
export type PresenceStatus = 'ONLINE' | 'AWAY' | 'IDLE' | 'DND' | 'OFFLINE';

export interface UserProfile {
  id: string;
  username: string;
  display_name: string;
  avatar_url?: string;
  about?: string;
  presence_status: PresenceStatus;
  last_seen?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  sequence_number: number;
  message_type: MessageType;
  content: string;
  media_url?: string;
  reply_to_message_id?: string;
  delivery_state: DeliveryState;
  is_edited: boolean;
  is_deleted_for_everyone: boolean;
  reactions: Record<string, string[]>;
  created_at: string;
}

export interface Conversation {
  id: string;
  type: 'direct' | 'group' | 'channel';
  title?: string;
  avatar_url?: string;
  last_message_preview?: string;
  last_message_timestamp?: string;
  unread_count: number;
  is_pinned: boolean;
  is_muted: boolean;
  participants: UserProfile[];
}
