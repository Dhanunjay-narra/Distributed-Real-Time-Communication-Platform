import React, { useState } from 'react';

/**
 * ChatTabNavigation - Horizontal tabs for filtering all chats, unread chats, favorites, and groups.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface ChatTabNavigationProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  className?: string;
  theme?: 'dark' | 'light';
}

export const ChatTabNavigation: React.FC<ChatTabNavigationProps> = ({
  activeTab = 'all',
  onTabChange,
  className = '',
  theme = 'dark'
}) => {
  return (
    <nav
      className={
        "flex items-center gap-2 p-2 rounded-xl border " +
        (theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-100 ' : 'bg-white border-slate-200 text-slate-900 ') +
        className
      }
    >
      <span className="text-xs font-semibold px-2">ChatTabNavigation</span>
    </nav>
  );
};
