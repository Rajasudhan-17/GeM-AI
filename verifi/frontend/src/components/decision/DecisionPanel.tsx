import React, { useState, useEffect } from 'react';
import { Gavel, Sparkles, CheckCircle2, XCircle, Clock, History } from 'lucide-react';
import { DecisionRecord, DecisionHistoryResponse, DecisionEnum } from '../../api/types';
import { generateDecisionReason, submitDecision, getDecision } from '../../api/client';

interface DecisionPanelProps {
  bidId: string;
  onDecisionSubmitted: () => void;
}

export const DecisionPanel: React.FC<DecisionPanelProps> = ({ bidId, onDecisionSubmitted }) => {
  const [reason, setReason] = useState('');
  const [isDrafting, setIsDrafting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [decisionData, setDecisionData] = useState<DecisionHistoryResponse | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    loadDecisionData();
  }, [bidId]);

  const loadDecisionData = async () => {
    try {
      const data = await getDecision(bidId);
      setDecisionData(data);
      if (data.current_decision) {
        setReason(data.current_decision.reason);
      }
    } catch {
      // No decision yet
    }
  };

  const handleAutoDraft = async () => {
    setIsDrafting(true);
    setError(null);
    try {
      const result = await generateDecisionReason(bidId);
      setReason(result.reason);
    } catch (err: any) {
      setError(err.message || 'Please run verification first before drafting reason.');
    } finally {
      setIsDrafting(false);
    }
  };

  const handleSubmit = async (decisionType: DecisionEnum) => {
    if (!reason || reason.trim().length < 5) {
      setError('Please enter a mandatory justification reason before submitting decision.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await submitDecision(bidId, decisionType, reason.trim());
      await loadDecisionData();
      onDecisionSubmitted();
    } catch (err: any) {
      setError(err.message || 'Failed to record decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentDecision = decisionData?.current_decision;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Gavel className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-800">Officer Procurement Decision</h2>
        </div>
        <div className="flex items-center gap-2">
          {decisionData && decisionData.history.length > 0 && (
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="text-xs font-semibold text-slate-500 hover:text-slate-700 bg-slate-100 px-2.5 py-1 rounded flex items-center gap-1"
            >
              <History className="w-3.5 h-3.5" />
              <span>History ({decisionData.history.length})</span>
            </button>
          )}
          <button
            onClick={handleAutoDraft}
            disabled={isDrafting}
            className="text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 px-3 py-1 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-600" />
            <span>{isDrafting ? 'Drafting...' : 'Auto-Draft Rationale'}</span>
          </button>
        </div>
      </div>

      {/* Decision Status Banner if already decided */}
      {currentDecision && (
        <div
          className={`p-3 rounded-xl border text-xs font-semibold flex items-start gap-2.5 ${
            currentDecision.decision === 'ACCEPTED'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
              : 'bg-rose-50 text-rose-800 border-rose-300'
          }`}
        >
          {currentDecision.decision === 'ACCEPTED' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
          )}
          <div>
            <div>
              OFFICER DECISION RECORDED: <strong>{currentDecision.decision}</strong> by {currentDecision.officer_name}
            </div>
            <div className="text-[11px] opacity-80 font-normal mt-0.5">
              Score at Decision: {currentDecision.score_at_decision}% • Risk: {currentDecision.risk_at_decision} • Recorded: {new Date(currentDecision.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      )}

      {/* Decision Rationale Input */}
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-bold text-slate-700 uppercase">
          Justification Reason (Mandatory):
        </label>
        <textarea
          rows={3}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Enter detailed evaluation findings or click 'Auto-Draft Rationale' above..."
          className="w-full text-xs p-3 rounded-xl border border-slate-300 bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none leading-relaxed"
        />
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 text-xs font-medium p-2.5 rounded-lg border border-rose-200">
          {error}
        </div>
      )}

      {/* Actions */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => handleSubmit('ACCEPTED')}
          disabled={isSubmitting}
          className="py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] shadow-sm transition-all flex items-center justify-center gap-1.5"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>ACCEPT BID</span>
        </button>

        <button
          onClick={() => handleSubmit('REJECTED')}
          disabled={isSubmitting}
          className="py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 active:scale-[0.99] shadow-sm transition-all flex items-center justify-center gap-1.5"
        >
          <XCircle className="w-4 h-4" />
          <span>REJECT BID</span>
        </button>
      </div>

      {/* Decision History Modal / Drawer */}
      {showHistory && decisionData && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex flex-col gap-2">
          <span className="text-[11px] font-bold text-slate-500 uppercase">Immutable Decision History</span>
          <div className="flex flex-col gap-2 max-h-36 overflow-y-auto">
            {decisionData.history.map((h) => (
              <div key={h.id} className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className={`font-bold ${h.decision === 'ACCEPTED' ? 'text-emerald-700' : 'text-rose-700'}`}>
                    {h.decision}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(h.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-slate-600">{h.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
