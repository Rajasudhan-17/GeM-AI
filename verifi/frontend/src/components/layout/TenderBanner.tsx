import React from 'react';
import { FileSpreadsheet, Building2, Tag } from 'lucide-react';
import { Tender } from '../../api/types';

interface TenderBannerProps {
  tender: Tender | null;
  isLoading: boolean;
}

export const TenderBanner: React.FC<TenderBannerProps> = ({ tender, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-slate-900 text-slate-400 px-6 py-3.5 rounded-xl text-sm flex items-center justify-between animate-pulse">
        <span>Loading tender details...</span>
      </div>
    );
  }

  if (!tender) {
    return (
      <div className="bg-slate-900 text-slate-400 px-6 py-3.5 rounded-xl text-sm flex items-center justify-between">
        <span>No active tender found.</span>
      </div>
    );
  }

  return (
    <section className="bg-slate-950 text-slate-100 px-6 py-3.5 rounded-xl shadow-md flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="bg-blue-500/20 p-2 rounded-lg text-blue-400">
          <FileSpreadsheet className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 uppercase font-semibold tracking-wider">Active Tender:</span>
            <span className="font-mono font-bold text-sky-400 text-sm">{tender.tender_number}</span>
          </div>
          <p className="text-sm font-semibold text-white">{tender.title}</p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs font-medium text-slate-300">
        <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
          <Tag className="w-3.5 h-3.5 text-slate-400" />
          <span>{tender.category}</span>
        </div>
        <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
          <Building2 className="w-3.5 h-3.5 text-slate-400" />
          <span>₹{(tender.estimated_value_inr / 10000000).toFixed(2)} Cr</span>
        </div>
        <div className="bg-blue-600/30 text-blue-300 px-2.5 py-1 rounded border border-blue-500/40 text-[11px] font-bold">
          {tender.requirements?.length || 8} MANDATORY CRITERIA
        </div>
      </div>
    </section>
  );
};
