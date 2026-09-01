import React from 'react';
import { Play, Users, AlertTriangle, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { Bidder, Bid, BidSummary } from '../../api/types';

interface SidebarProps {
  bidders: Bidder[];
  bids: Bid[];
  selectedBidderId: string | null;
  selectedBidSummary: BidSummary | null;
  onSelectBidder: (bidderId: string) => void;
  onRunVerification: () => void;
  isVerifying: boolean;
  isLoading: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  bidders,
  bids,
  selectedBidderId,
  selectedBidSummary,
  onSelectBidder,
  onRunVerification,
  isVerifying,
  isLoading,
}) => {
  const getRiskBadge = (risk?: string) => {
    switch (risk) {
      case 'LOW':
        return <span className="bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2 py-0.5 rounded border border-emerald-300">LOW RISK</span>;
      case 'MEDIUM':
        return <span className="bg-amber-100 text-amber-800 text-[11px] font-bold px-2 py-0.5 rounded border border-amber-300">MEDIUM RISK</span>;
      case 'HIGH':
        return <span className="bg-rose-100 text-rose-800 text-[11px] font-bold px-2 py-0.5 rounded border border-rose-300">HIGH RISK</span>;
      default:
        return <span className="bg-slate-100 text-slate-600 text-[11px] font-medium px-2 py-0.5 rounded border border-slate-200">NOT RUN</span>;
    }
  };

  const selectedBidder = bidders.find((b) => b.id === selectedBidderId);

  return (
    <aside className="w-full lg:w-80 flex flex-col gap-5 shrink-0">
      {/* Bidders List Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-800">Primary MVP Bidders</h2>
          </div>
          <span className="bg-slate-100 text-slate-600 text-xs font-semibold px-2 py-0.5 rounded-full">
            {bidders.length}
          </span>
        </div>

        {isLoading ? (
          <div className="flex flex-col gap-2.5">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-slate-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="flex flex-col gap-2.5">
            {bidders.map((bidder) => {
              const bid = bids.find((b) => b.bidder_id === bidder.id);
              const isSelected = bidder.id === selectedBidderId;
              const hasScore = bid?.latest_score !== null && bid?.latest_score !== undefined;

              return (
                <button
                  key={bidder.id}
                  onClick={() => onSelectBidder(bidder.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    isSelected
                      ? 'bg-blue-50/80 border-blue-500 shadow-sm ring-1 ring-blue-500/20'
                      : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="truncate">
                      <p className="text-sm font-bold text-slate-900 truncate">{bidder.name}</p>
                      <p className="font-mono text-xs text-slate-500 font-medium">{bidder.id}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-slate-100 text-xs">
                    <span className="font-bold text-slate-800">
                      {hasScore ? `${bid?.latest_score}%` : 'Pending'}
                    </span>
                    {getRiskBadge(bid?.latest_risk_level)}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Bidder Summary & Action Card */}
      {selectedBidder && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <span className="text-xs uppercase font-bold text-slate-400 tracking-wider">Selected Bidder</span>
            <span className="font-mono text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              {selectedBidSummary?.bid_id || 'BID'}
            </span>
          </div>

          <div>
            <h3 className="text-base font-bold text-slate-900 leading-tight">{selectedBidder.name}</h3>
            <p className="text-xs text-slate-500 mt-0.5">{selectedBidder.legal_entity_type}</p>
            <p className="font-mono text-xs text-slate-400 mt-1">ID: {selectedBidder.id}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80 flex flex-col">
              <span className="text-[11px] font-semibold text-slate-500 uppercase">Compliance Score</span>
              <span className="text-2xl font-black text-slate-900 mt-1">
                {selectedBidSummary?.score !== null && selectedBidSummary?.score !== undefined
                  ? `${selectedBidSummary.score}%`
                  : '--%'}
              </span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase">Risk Level</span>
              <div className="mt-1">
                {getRiskBadge(selectedBidSummary?.risk_level)}
              </div>
            </div>
          </div>

          {selectedBidSummary?.latest_decision && (
            <div
              className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center gap-2 ${
                selectedBidSummary.latest_decision === 'ACCEPTED'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-rose-50 text-rose-800 border-rose-200'
              }`}
            >
              {selectedBidSummary.latest_decision === 'ACCEPTED' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              )}
              <span>Decision: <strong>{selectedBidSummary.latest_decision}</strong></span>
            </div>
          )}

          <button
            onClick={onRunVerification}
            disabled={isVerifying}
            className={`w-full py-3 px-4 rounded-lg font-bold text-sm flex items-center justify-center gap-2 shadow-sm transition-all ${
              isVerifying
                ? 'bg-blue-300 text-white cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:scale-[0.99] text-white shadow-blue-500/20'
            }`}
          >
            <Play className={`w-4 h-4 fill-current ${isVerifying ? 'animate-spin' : ''}`} />
            <span>{isVerifying ? 'Verification in progress...' : 'RUN VERIFICATION PIPELINE'}</span>
          </button>
        </div>
      )}
    </aside>
  );
};
