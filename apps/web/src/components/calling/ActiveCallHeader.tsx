import React, { useState } from 'react';

/**
 * ActiveCallHeader - Call participant count, duration timer, and connection encryption badge.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface ActiveCallHeaderProps {
  onAction?: (action: string, payload?: any) => void;
  className?: string;
  theme?: 'dark' | 'light';
}

export const ActiveCallHeader: React.FC<ActiveCallHeaderProps> = ({
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
        <h4 className="text-xs font-semibold">ActiveCallHeader</h4>
        <p className="text-[10px] text-slate-400">Call participant count, duration timer, and connection encryption badge</p>
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
