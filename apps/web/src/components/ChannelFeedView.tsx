import React, { useState, useEffect, useRef } from 'react';

/**
 * ChannelFeedView - Broadcast channels feed view with subscriber counter and reactions.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface ChannelFeedViewProps {
  isOpen?: boolean;
  onClose?: () => void;
  onSubmit?: (data: any) => void;
  className?: string;
  theme?: 'dark' | 'light';
  metadata?: Record<string, any>;
}

export const ChannelFeedView: React.FC<ChannelFeedViewProps> = ({
  isOpen = true,
  onClose,
  onSubmit,
  className = '',
  theme = 'dark',
  metadata = {}
}) => {
  const [loading, setLoading] = useState(false);
  const [activeItem, setActiveItem] = useState<string | null>(null);
  const [itemsList, setItemsList] = useState<Array<{ id: string; title: string; timestamp: number }>>([
    { id: '1', title: 'Default Item 1', timestamp: Date.now() },
    { id: '2', title: 'Default Item 2', timestamp: Date.now() - 60000 }
  ]);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && onClose) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleActionClick = (id: string) => {
    setActiveItem(id);
    if (onSubmit) {
      onSubmit({ action: 'ChannelFeedView_ACTION', targetId: id, timestamp: Date.now() });
    }
  };

  if (!isOpen) return null;

  return (
    <div
      ref={containerRef}
      className={
        "rounded-2xl border p-4 shadow-xl backdrop-blur transition-all " +
        (theme === 'dark' ? 'bg-slate-900/90 border-slate-800 text-slate-100 ' : 'bg-white/90 border-slate-200 text-slate-900 ') +
        className
      }
    >
      <div className="flex items-center justify-between border-b border-slate-800/50 pb-3 mb-4">
        <h3 className="font-semibold text-base tracking-tight">ChannelFeedView</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
            aria-label="Close"
          >
            ✕
          </button>
        )}
      </div>

      <div className="space-y-3">
        <p className="text-xs text-slate-400 leading-relaxed">Broadcast channels feed view with subscriber counter and reactions</p>
        <div className="divide-y divide-slate-800/40 rounded-xl bg-slate-950/40 p-2">
          {itemsList.map((item) => (
            <div
              key={item.id}
              onClick={() => handleActionClick(item.id)}
              className={
                "flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition " +
                (activeItem === item.id ? 'bg-indigo-600/30 text-indigo-300' : 'hover:bg-slate-800/60')
              }
            >
              <span className="text-sm font-medium">{item.title}</span>
              <span className="text-[10px] opacity-60">
                {new Date(item.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-end gap-2 pt-3 border-t border-slate-800/50">
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-xl px-4 py-2 text-xs font-medium text-slate-400 hover:bg-slate-800 transition"
          >
            Cancel
          </button>
        )}
        <button
          onClick={() => handleActionClick('SUBMIT_PRIMARY')}
          disabled={loading}
          className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Confirm Action'}
        </button>
      </div>
    </div>
  );
};
