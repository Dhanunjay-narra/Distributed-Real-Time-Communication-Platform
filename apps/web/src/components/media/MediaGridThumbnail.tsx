import React, { useState } from 'react';

/**
 * MediaGridThumbnail - Square media gallery grid item with video duration and GIF badge.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface MediaGridThumbnailProps {
  onAction?: (action: string, payload?: any) => void;
  className?: string;
  theme?: 'dark' | 'light';
}

export const MediaGridThumbnail: React.FC<MediaGridThumbnailProps> = ({
  onAction,
  className = '',
  theme = 'dark'
}) => {
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <div
      className={
        "rounded-xl overflow-hidden border shadow-sm transition-all " +
        (theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-100 ' : 'bg-white border-slate-200 text-slate-900 ') +
        className
      }
    >
      <div className="p-3">
        <h4 className="text-xs font-semibold">MediaGridThumbnail</h4>
        <p className="text-[10px] text-slate-400">Square media gallery grid item with video duration and GIF badge</p>
      </div>
      <div className="flex justify-end p-2 bg-slate-950/20 border-t border-slate-800/40">
        <button
          onClick={() => {
            setIsLoaded(!isLoaded);
            if (onAction) onAction('INTERACT', { loaded: !isLoaded });
          }}
          className="rounded-lg bg-indigo-600 px-3 py-1 text-[10px] font-semibold text-white hover:bg-indigo-500 transition"
        >
          View
        </button>
      </div>
    </div>
  );
};
