import React from 'react';
import { Check, Loader2 } from 'lucide-react';
import { VerificationRun } from '../../api/types';

interface StageProgressProps {
  run: VerificationRun | null;
  isVerifying: boolean;
}

const STAGES = [
  { key: 'PENDING', label: 'Pending' },
  { key: 'RUNNING', label: 'Running' },
  { key: 'OCR', label: 'OCR Extraction' },
  { key: 'EXTRACTING', label: 'Fact Parsing' },
  { key: 'VERIFYING', label: 'Govt Sources' },
  { key: 'RULE_EVALUATION', label: 'Rules' },
  { key: 'SCORING', label: 'Score Engine' },
  { key: 'AI_ANALYSIS', label: 'AI Synthesis' },
  { key: 'COMPLETED', label: 'Completed' },
];

export const StageProgress: React.FC<StageProgressProps> = ({ run, isVerifying }) => {
  if (!run && !isVerifying) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-bold text-slate-800">Verification Pipeline Status</h2>
          <span className="font-mono text-xs text-slate-400">Status: Standby</span>
        </div>
        <p className="text-xs text-slate-500 italic">
          Click "RUN VERIFICATION PIPELINE" to trigger the multi-stage OCR, government cross-checks, and deterministic rules.
        </p>
      </div>
    );
  }

  const currentStageKey = run?.current_stage || 'PENDING';
  const stageKeys = STAGES.map((s) => s.key);
  const currentIdx = stageKeys.indexOf(currentStageKey);
  const isCompleted = run?.status === 'COMPLETED';
  const isFailed = run?.status === 'FAILED';
  const progressPct = run?.progress_pct || 0;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Verification Pipeline Progression</h2>
          <span className="font-mono text-xs text-slate-500">
            Run ID: <strong className="text-blue-600">{run?.id || 'Initializing...'}</strong>
          </span>
        </div>
        <span
          className={`text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
            isCompleted
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
              : isFailed
              ? 'bg-rose-100 text-rose-800 border border-rose-300'
              : 'bg-blue-100 text-blue-800 border border-blue-300 animate-pulse'
          }`}
        >
          {run?.status || 'PENDING'}
        </span>
      </div>

      {/* Steps visualization */}
      <div className="relative pt-2">
        <div className="hidden sm:grid grid-cols-9 gap-1 text-center relative z-10">
          {STAGES.map((stage, idx) => {
            const isPast = idx < currentIdx || isCompleted;
            const isCurrent = idx === currentIdx && !isCompleted && !isFailed;

            return (
              <div key={stage.key} className="flex flex-col items-center gap-1.5">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    isPast
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : isCurrent
                      ? 'bg-blue-600 text-white ring-4 ring-blue-100 shadow-md'
                      : 'bg-slate-100 text-slate-400 border border-slate-200'
                  }`}
                >
                  {isPast ? (
                    <Check className="w-3.5 h-3.5 stroke-[3]" />
                  ) : isCurrent ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <span>{idx + 1}</span>
                  )}
                </div>
                <span
                  className={`text-[11px] font-semibold tracking-tight ${
                    isPast
                      ? 'text-emerald-700'
                      : isCurrent
                      ? 'text-blue-700 font-bold'
                      : 'text-slate-400'
                  }`}
                >
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Progress Bar Line */}
        <div className="w-full bg-slate-100 h-2 rounded-full mt-3 overflow-hidden border border-slate-200/80">
          <div
            className={`h-full transition-all duration-300 ${
              isCompleted
                ? 'bg-emerald-500'
                : isFailed
                ? 'bg-rose-500'
                : 'bg-gradient-to-r from-blue-600 to-sky-400'
            }`}
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>
    </div>
  );
};
