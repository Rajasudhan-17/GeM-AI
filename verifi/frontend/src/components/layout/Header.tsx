import React from 'react';
import { ShieldCheck, Server } from 'lucide-react';
import { HealthResponse } from '../../api/types';

interface HeaderProps {
  health: HealthResponse | null;
  isHealthLoading: boolean;
  healthError: string | null;
}

export const Header: React.FC<HeaderProps> = ({ health, isHealthLoading, healthError }) => {
  const isOnline = !!health && health.status === 'healthy';

  return (
    <header className="bg-white border border-slate-200 rounded-xl px-6 py-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-4">
        <div className="bg-gradient-to-br from-blue-900 to-blue-600 text-white font-extrabold text-lg px-3.5 py-1.5 rounded-lg shadow-inner flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-blue-200" />
          <span>VERIFI</span>
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-900 leading-tight">
            GeM Bid Compliance Verification Engine
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Phase 1 MVP • Deterministic Rule Engine • Zero Database Mode
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border ${
            isOnline
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-rose-50 text-rose-700 border-rose-200'
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
            }`}
          />
          <Server className="w-3.5 h-3.5 opacity-70" />
          <span>
            {isHealthLoading
              ? 'Connecting...'
              : isOnline
              ? `Backend: Connected (v${health?.version || '1.0'})`
              : 'Backend: Unavailable (Port 8000)'}
          </span>
        </div>
      </div>
    </header>
  );
};
