import React, { useState } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, HelpCircle, ChevronRight, ShieldCheck } from 'lucide-react';
import { VerificationCheck } from '../../api/types';
import { CheckDetailModal } from './CheckDetailModal';

interface ChecksListProps {
  checks: VerificationCheck[];
  isLoading: boolean;
}

export const ChecksList: React.FC<ChecksListProps> = ({ checks, isLoading }) => {
  const [selectedCheck, setSelectedCheck] = useState<VerificationCheck | null>(null);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PASS':
        return (
          <span className="bg-emerald-50 text-emerald-700 border border-emerald-300 text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>PASS</span>
          </span>
        );
      case 'FAIL':
        return (
          <span className="bg-rose-50 text-rose-700 border border-rose-300 text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>FAIL</span>
          </span>
        );
      case 'REVIEW':
        return (
          <span className="bg-amber-50 text-amber-700 border border-amber-300 text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>REVIEW</span>
          </span>
        );
      default:
        return (
          <span className="bg-slate-50 text-slate-700 border border-slate-300 text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>{status}</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-800">Deterministic Compliance Checklist</h2>
        </div>
        <span className="text-xs text-slate-400 font-medium">Click any check to inspect fact comparison</span>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-24 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : checks.length === 0 ? (
        <div className="text-center py-10 text-slate-400 text-sm italic">
          No verification checks available. Run the verification pipeline to evaluate rules.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {checks.map((check) => (
            <div
              key={check.id}
              onClick={() => setSelectedCheck(check)}
              className="group p-3.5 rounded-xl border border-slate-200 hover:border-blue-400 bg-white hover:bg-blue-50/20 cursor-pointer transition-all shadow-sm hover:shadow flex flex-col justify-between gap-2"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {check.check_name}
                  </h4>
                  <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400 mt-0.5">
                    <span>{check.rule_code}</span>
                    <span>•</span>
                    <span>{check.document_type}</span>
                  </div>
                </div>
                {getStatusBadge(check.status)}
              </div>

              <p className="text-xs text-slate-600 font-medium line-clamp-2 leading-relaxed mt-1">
                {check.reason}
              </p>

              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400 font-medium">
                <span>Weight: {check.evidence?.rule_weight || 15} pts</span>
                <span className="text-blue-600 flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform font-semibold">
                  Inspect Facts <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      <CheckDetailModal check={selectedCheck} onClose={() => setSelectedCheck(null)} />
    </div>
  );
};
