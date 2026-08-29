import React, { useState } from 'react';

/**
 * StatusTextComposer - Status text composer with custom background gradient and font picker.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface StatusTextComposerProps {
  onClose?: () => void;
  className?: string;
  theme?: 'dark' | 'light';
}

export const StatusTextComposer: React.FC<StatusTextComposerProps> = ({
  onClose,
  className = '',
  theme = 'dark'
}) => {
  return (
    <div
      className={
        "rounded-2xl border p-4 shadow-xl backdrop-blur transition-all " +
        (theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-100 ' : 'bg-white border-slate-200 text-slate-900 ') +
        className
      }
    >
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/40 mb-3">
        <h4 className="text-sm font-semibold">StatusTextComposer</h4>
        {onClose && (
          <button onClick={onClose} className="text-xs text-slate-400 hover:text-slate-200">✕</button>
        )}
      </div>
      <p className="text-xs text-slate-400">Status text composer with custom background gradient and font picker</p>
    </div>
  );
};
