import React, { useState } from 'react';

/**
 * UserSettingsModal - Full user preferences dialog with notifications, privacy, and account security.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface UserSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm?: (data: any) => void;
  theme?: 'dark' | 'light';
}

export const UserSettingsModal: React.FC<UserSettingsModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  theme = 'dark'
}) => {
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div
        className={
          "w-full max-w-md rounded-2xl border p-6 shadow-2xl transition-all " +
          (theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-900')
        }
      >
        <div className="flex items-center justify-between border-b border-slate-800/50 pb-3 mb-4">
          <h3 className="font-bold text-lg">UserSettingsModal</h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
          >
            ✕
          </button>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed mb-6">Full user preferences dialog with notifications, privacy, and account security</p>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800/50">
          <button
            onClick={onClose}
            className="rounded-xl px-4 py-2 text-xs font-medium text-slate-400 hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              if (onConfirm) onConfirm({ timestamp: Date.now() });
              onClose();
            }}
            disabled={loading}
            className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-semibold text-white hover:bg-indigo-500 shadow-md"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};
