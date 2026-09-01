import React from 'react';
import { ScrollText, RefreshCw, Hash, User, Clock } from 'lucide-react';
import { AuditEvent } from '../../api/types';

interface AuditTrailProps {
  events: AuditEvent[];
  isLoading: boolean;
  onRefresh: () => void;
}

export const AuditTrail: React.FC<AuditTrailProps> = ({ events, isLoading, onRefresh }) => {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <ScrollText className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-800">Immutable Audit Trail (SHA-256 Chained)</h2>
        </div>
        <button
          onClick={onRefresh}
          className="text-xs font-semibold text-slate-500 hover:text-slate-700 bg-slate-100 hover:bg-slate-200/80 px-2.5 py-1 rounded-lg flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : events.length === 0 ? (
        <div className="text-center py-6 text-slate-400 text-sm italic">
          No audit events recorded for this bid yet.
        </div>
      ) : (
        <div className="flex flex-col gap-2 max-h-60 overflow-y-auto pr-1">
          {events.map((event) => (
            <div
              key={event.id}
              className="p-2.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 flex items-center justify-between text-xs transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
                <div>
                  <div className="font-bold text-slate-900">{event.action}</div>
                  <div className="flex items-center gap-2 text-[11px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3 text-slate-400" />
                      {event.actor}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-right font-mono text-[10px] text-slate-400">
                <div className="text-slate-600 font-medium">ID: {event.id}</div>
                <div className="flex items-center justify-end gap-1 text-slate-400">
                  <Hash className="w-2.5 h-2.5" />
                  <span>{event.event_hash ? event.event_hash.substring(0, 16) : '-'}...</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
