import React, { useState, useEffect } from 'react';

export const AdminDashboard: React.FC = () => {
  const [telemetry, setTelemetry] = useState({
    total_registered_users: 1420,
    total_conversations: 850,
    persisted_messages: 94230,
    pending_reports_queue: 3,
    cluster_status: "ONLINE"
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <header className="mb-8 border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-extrabold text-indigo-400">Chatbot Operations & Moderation Control Center</h1>
        <p className="text-slate-400 text-sm mt-1">Distributed cluster telemetry and moderation resolution portal</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Registered Users</p>
          <p className="text-3xl font-bold text-slate-100 mt-2">{telemetry.total_registered_users.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Active Conversations</p>
          <p className="text-3xl font-bold text-slate-100 mt-2">{telemetry.total_conversations.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Messages Processed</p>
          <p className="text-3xl font-bold text-indigo-400 mt-2">{telemetry.persisted_messages.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Pending Reports</p>
          <p className="text-3xl font-bold text-amber-400 mt-2">{telemetry.pending_reports_queue}</p>
        </div>
      </div>
    </div>
  );
};
