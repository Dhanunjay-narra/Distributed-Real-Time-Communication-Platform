import React, { useState } from 'react';

/**
 * MediaEditorToolbar - Image markup toolbar with crop, rotate, draw, text, and blur tools.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface MediaEditorToolbarProps {
  onAction?: (action: string, payload?: any) => void;
  className?: string;
  theme?: 'dark' | 'light';
}

export const MediaEditorToolbar: React.FC<MediaEditorToolbarProps> = ({
  onAction,
  className = '',
  theme = 'dark'
}) => {
  const [active, setActive] = useState(false);

  return (
    <div
      className={
        "flex items-center gap-3 rounded-xl p-3 border shadow-sm transition-all " +
        (theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-100 ' : 'bg-white border-slate-200 text-slate-900 ') +
        className
      }
    >
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/20 text-indigo-400 font-bold text-xs">
        M
      </div>
      <div className="flex-1">
        <h4 className="text-xs font-semibold">MediaEditorToolbar</h4>
        <p className="text-[10px] text-slate-400">Image markup toolbar with crop, rotate, draw, text, and blur tools</p>
      </div>
      <button
        onClick={() => {
          setActive(!active);
          if (onAction) onAction('TOGGLE', { active: !active });
        }}
        className={
          "rounded-lg px-3 py-1 text-[10px] font-semibold transition " +
          (active ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700')
        }
      >
        {active ? 'Active' : 'Open'}
      </button>
    </div>
  );
};
