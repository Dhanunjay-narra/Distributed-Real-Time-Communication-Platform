import React, { useState } from 'react';

/**
 * StorageDataSettings - Network usage statistics, storage cleaner, and auto-delete cache.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface StorageDataSettingsProps {
  theme?: 'dark' | 'light';
  onSave?: (settings: any) => void;
}

export const StorageDataSettings: React.FC<StorageDataSettingsProps> = ({
  theme = 'dark',
  onSave
}) => {
  const [enabled, setEnabled] = useState(true);

  return (
    <div
      className={
        "rounded-2xl border p-6 shadow-sm transition-all " +
        (theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-900')
      }
    >
      <div className="flex items-center justify-between border-b border-slate-800/50 pb-4 mb-4">
        <div>
          <h3 className="font-bold text-base">StorageDataSettings</h3>
          <p className="text-xs text-slate-400 mt-0.5">Network usage statistics, storage cleaner, and auto-delete cache</p>
        </div>
        <button
          onClick={() => {
            setEnabled(!enabled);
            if (onSave) onSave({ enabled: !enabled });
          }}
          className={
            "rounded-xl px-4 py-2 text-xs font-semibold transition " +
            (enabled ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300')
          }
        >
          {enabled ? 'Enabled' : 'Disabled'}
        </button>
      </div>
      <div className="space-y-3 text-xs text-slate-400">
        <p>Configured settings and preferences for this device.</p>
      </div>
    </div>
  );
};
