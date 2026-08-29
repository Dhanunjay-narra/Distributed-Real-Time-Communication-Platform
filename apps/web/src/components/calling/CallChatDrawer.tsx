import React, { useState } from 'react';

/**
 * CallChatDrawer - In-call text chat sidebar with quick reaction emojis and raise-hand feature.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface CallChatDrawerProps {
  onAction?: (action: string, payload?: any) => void;
  className?: string;
  theme?: 'dark' | 'light';
}

export const CallChatDrawer: React.FC<CallChatDrawerProps> = ({
  onAction,
  className = '',
  theme = 'dark'
}) => {
  const [active, setActive] = useState(false);

  return (
    <div
      className={
        "flex items-center justify-between rounded-xl p-3 border shadow-sm transition-all " +
        (theme === 'dark' ? 'bg-slate-900/90 border-slate-800 text-slate-100 ' : 'bg-white/90 border-slate-200 text-slate-900 ') +
        className
      }
    >
      <div>
        <h4 className="text-xs font-semibold">CallChatDrawer</h4>
        <p className="text-[10px] text-slate-400">In-call text chat sidebar with quick reaction emojis and raise-hand feature</p>
      </div>
      <button
        onClick={() => {
          setActive(!active);
          if (onAction) onAction('TRIGGER', { active: !active });
        }}
        className="rounded-lg bg-indigo-600 px-3 py-1 text-[10px] font-semibold text-white hover:bg-indigo-500 transition"
      >
        Action
      </button>
    </div>
  );
};
