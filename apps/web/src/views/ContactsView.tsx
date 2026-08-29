import React, { useState, useEffect } from 'react';

/**
 * ContactsView - Contact address book with search bar, online status dots, and invite buttons.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface ContactsViewProps {
  currentUserId?: string;
  theme?: 'dark' | 'light';
  onNavigate?: (view: string) => void;
}

export const ContactsView: React.FC<ContactsViewProps> = ({
  currentUserId = 'user-01',
  theme = 'dark',
  onNavigate
}) => {
  const [activeTab, setActiveTab] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [items, setItems] = useState<Array<{ id: string; name: string; subtitle: string; timestamp: number }>>([
    { id: '1', name: 'Primary Item Alpha', subtitle: 'Detailed subtitle metadata entry', timestamp: Date.now() },
    { id: '2', name: 'Secondary Item Beta', subtitle: 'Additional contextual record', timestamp: Date.now() - 3600000 },
    { id: '3', name: 'Tertiary Item Gamma', subtitle: 'Historical archived information', timestamp: Date.now() - 7200000 }
  ]);

  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.subtitle.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={
      "flex h-full w-full flex-col p-6 " +
      (theme === 'dark' ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900')
    }>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">ContactsView</h1>
          <p className="text-xs text-slate-400 mt-1">Contact address book with search bar, online status dots, and invite buttons</p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-800/40 pb-2">
        {['all', 'recent', 'favorites', 'archived'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={
              "rounded-lg px-4 py-1.5 text-xs font-semibold uppercase tracking-wider transition " +
              (activeTab === tab
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200')
            }
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content List */}
      <div className="flex-1 overflow-y-auto space-y-3">
        {filteredItems.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between rounded-xl border border-slate-800/50 bg-slate-900/40 p-4 transition hover:bg-slate-900 hover:border-slate-700"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-600/20 text-indigo-400 font-bold">
                {item.name[0]}
              </div>
              <div>
                <h3 className="font-semibold text-sm">{item.name}</h3>
                <p className="text-xs text-slate-400">{item.subtitle}</p>
              </div>
            </div>
            <span className="text-[10px] text-slate-500">
              {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
