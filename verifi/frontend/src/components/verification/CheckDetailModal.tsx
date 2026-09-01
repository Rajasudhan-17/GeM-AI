import React from 'react';
import { X, CheckCircle, AlertTriangle, AlertCircle, HelpCircle, FileText, Database } from 'lucide-react';
import { VerificationCheck } from '../../api/types';

interface CheckDetailModalProps {
  check: VerificationCheck | null;
  onClose: () => void;
}

export const CheckDetailModal: React.FC<CheckDetailModalProps> = ({ check, onClose }) => {
  if (!check) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PASS':
        return <CheckCircle className="w-5 h-5 text-emerald-600" />;
      case 'FAIL':
        return <AlertCircle className="w-5 h-5 text-rose-600" />;
      case 'REVIEW':
        return <AlertTriangle className="w-5 h-5 text-amber-600" />;
      default:
        return <HelpCircle className="w-5 h-5 text-slate-400" />;
    }
  };

  const getBadgeStyle = (status: string) => {
    switch (status) {
      case 'PASS':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'FAIL':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'REVIEW':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  const discrepancies = check.fact_comparison?.discrepancies || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal Card */}
      <div className="relative bg-white border border-slate-200 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl z-10 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-3">
            {getStatusIcon(check.status)}
            <div>
              <h3 className="text-base font-bold text-slate-900">{check.check_name}</h3>
              <p className="font-mono text-xs text-slate-500 font-medium">
                Rule ID: {check.rule_code} • Requirement: {check.requirement_code}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 flex flex-col gap-5">
          {/* Status and Reason Banner */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Evaluation Result</span>
              <span className={`text-xs font-bold px-2.5 py-1 rounded border ${getBadgeStyle(check.status)}`}>
                {check.status}
              </span>
            </div>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-sm text-slate-800 leading-relaxed font-medium">
              {check.reason}
            </div>
          </div>

          {/* Discrepancy Alert if any */}
          {discrepancies.length > 0 && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2 text-rose-800 font-bold text-sm">
                <AlertCircle className="w-4 h-4 text-rose-600" />
                <span>Detected Inconsistencies & Discrepancies</span>
              </div>
              <ul className="list-disc list-inside text-xs text-rose-900 font-medium space-y-1">
                {discrepancies.map((disc, idx) => (
                  <li key={idx} className="font-mono">{disc}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Side-by-Side Fact Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Extracted Facts */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <FileText className="w-4 h-4 text-blue-600" />
                <span>Submitted Document Facts</span>
              </div>
              <pre className="bg-white p-3 rounded-lg border border-slate-200 text-[11px] font-mono text-slate-800 overflow-x-auto">
                {JSON.stringify(check.extracted_facts || {}, null, 2)}
              </pre>
            </div>

            {/* Authoritative Source Facts */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <Database className="w-4 h-4 text-indigo-600" />
                <span>Authoritative Source Facts</span>
              </div>
              <pre className="bg-white p-3 rounded-lg border border-slate-200 text-[11px] font-mono text-slate-800 overflow-x-auto">
                {JSON.stringify(check.source_facts || {}, null, 2)}
              </pre>
            </div>
          </div>

          {/* Evidence Meta */}
          <div className="text-xs text-slate-400 font-mono flex items-center justify-between pt-2 border-t border-slate-100">
            <span>Provider: {check.evidence?.provider || 'INTERNAL'}</span>
            <span>Evaluated: {new Date(check.evaluated_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
