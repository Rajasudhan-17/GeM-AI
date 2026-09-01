import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/layout/Header';
import { TenderBanner } from './components/layout/TenderBanner';
import { Sidebar } from './components/layout/Sidebar';
import { StageProgress } from './components/verification/StageProgress';
import { ChecksList } from './components/verification/ChecksList';
import { DocumentList } from './components/documents/DocumentList';
import { AIChatPanel } from './components/ai/AIChatPanel';
import { DecisionPanel } from './components/decision/DecisionPanel';
import { AuditTrail } from './components/audit/AuditTrail';

import {
  HealthResponse,
  Tender,
  Bidder,
  Bid,
  BidSummary,
  VerificationCheck,
  DocumentItem,
  VerificationRun,
  AuditEvent,
} from './api/types';

import {
  getHealth,
  getTenders,
  getBidders,
  getBids,
  getBidSummary,
  getBidChecks,
  getBidDocuments,
  startVerification,
  getVerificationRun,
  getAuditTrail,
} from './api/client';

export const App: React.FC = () => {
  // Global & Layout State
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState<string | null>(null);

  const [tender, setTender] = useState<Tender | null>(null);
  const [isTenderLoading, setIsTenderLoading] = useState(true);

  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [bids, setBids] = useState<Bid[]>([]);
  const [isBiddersLoading, setIsBiddersLoading] = useState(true);

  // Selected Bidder / Bid State
  const [selectedBidderId, setSelectedBidderId] = useState<string | null>(null);
  const [selectedBidSummary, setSelectedBidSummary] = useState<BidSummary | null>(null);
  const [checks, setChecks] = useState<VerificationCheck[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [currentRun, setCurrentRun] = useState<VerificationRun | null>(null);

  // Loading States
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isAuditLoading, setIsAuditLoading] = useState(false);

  // Polling ref to prevent interval leaks
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // 1. Initial Load: Health, Tender, Bidders
  useEffect(() => {
    checkBackendHealth();
    loadTenders();
    loadBiddersList();

    const healthInterval = setInterval(checkBackendHealth, 10000);
    return () => {
      clearInterval(healthInterval);
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  // 2. When Selected Bidder Changes, Load Details
  useEffect(() => {
    if (selectedBidderId) {
      loadBidderDetails(selectedBidderId);
    }
  }, [selectedBidderId]);

  const checkBackendHealth = async () => {
    setIsHealthLoading(true);
    try {
      const data = await getHealth();
      setHealth(data);
      setHealthError(null);
    } catch (err: any) {
      setHealth(null);
      setHealthError(err.message || 'Backend connection failed');
    } finally {
      setIsHealthLoading(false);
    }
  };

  const loadTenders = async () => {
    setIsTenderLoading(true);
    try {
      const data = await getTenders();
      if (data.length > 0) {
        setTender(data[0]);
      }
    } catch (err) {
      console.error('Failed to load tenders:', err);
    } finally {
      setIsTenderLoading(false);
    }
  };

  const loadBiddersList = async () => {
    setIsBiddersLoading(true);
    try {
      const [biddersData, bidsData] = await Promise.all([getBidders(), getBids()]);
      setBidders(biddersData);
      setBids(bidsData);

      // Auto-select first bidder if none selected
      if (biddersData.length > 0 && !selectedBidderId) {
        setSelectedBidderId(biddersData[0].id);
      }
    } catch (err) {
      console.error('Failed to load bidders:', err);
    } finally {
      setIsBiddersLoading(false);
    }
  };

  const loadBidderDetails = async (bidderId: string) => {
    const matchingBid = bids.find((b) => b.bidder_id === bidderId);
    if (!matchingBid) return;

    setIsDetailsLoading(true);
    try {
      const [summaryData, checksData, docsData, auditData] = await Promise.all([
        getBidSummary(matchingBid.id),
        getBidChecks(matchingBid.id),
        getBidDocuments(matchingBid.id),
        getAuditTrail(matchingBid.id),
      ]);

      setSelectedBidSummary(summaryData);
      setChecks(checksData);
      setDocuments(docsData);
      setAuditEvents(auditData);

      // If there is an existing verification run, load its status
      if (matchingBid.latest_verification_run_id) {
        const runData = await getVerificationRun(matchingBid.latest_verification_run_id);
        setCurrentRun(runData);
      } else {
        setCurrentRun(null);
      }
    } catch (err) {
      console.error('Failed to load bidder details:', err);
    } finally {
      setIsDetailsLoading(false);
    }
  };

  // 3. Trigger Background Verification Pipeline
  const handleRunVerification = async () => {
    const matchingBid = bids.find((b) => b.bidder_id === selectedBidderId);
    if (!matchingBid || isVerifying) return;

    setIsVerifying(true);
    try {
      const startRes = await startVerification(matchingBid.id);
      
      // Start Polling backend verification run
      startPipelinePolling(startRes.run_id, matchingBid.id);
    } catch (err: any) {
      alert(`Verification start failed: ${err.message}`);
      setIsVerifying(false);
    }
  };

  const startPipelinePolling = (runId: string, bidId: string) => {
    if (pollingRef.current) clearInterval(pollingRef.current);

    pollingRef.current = setInterval(async () => {
      try {
        const run = await getVerificationRun(runId);
        setCurrentRun(run);

        if (run.status === 'COMPLETED' || run.status === 'FAILED') {
          if (pollingRef.current) clearInterval(pollingRef.current);
          setIsVerifying(false);

          // Refresh all data from backend
          await Promise.all([
            loadBiddersList(),
            loadBidderDetails(selectedBidderId!),
          ]);
        }
      } catch (err) {
        console.error('Error polling verification run:', err);
        if (pollingRef.current) clearInterval(pollingRef.current);
        setIsVerifying(false);
      }
    }, 800);
  };

  const handleRefreshAudit = async () => {
    const matchingBid = bids.find((b) => b.bidder_id === selectedBidderId);
    if (!matchingBid) return;

    setIsAuditLoading(true);
    try {
      const data = await getAuditTrail(matchingBid.id);
      setAuditEvents(data);
    } catch (err) {
      console.error('Failed to refresh audit trail:', err);
    } finally {
      setIsAuditLoading(false);
    }
  };

  const currentBid = bids.find((b) => b.bidder_id === selectedBidderId);
  const currentBidder = bidders.find((b) => b.id === selectedBidderId);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-6">
      {/* Top Header */}
      <Header health={health} isHealthLoading={isHealthLoading} healthError={healthError} />

      {/* Tender Banner */}
      <TenderBanner tender={tender} isLoading={isTenderLoading} />

      {/* Main Workspace Layout */}
      <div className="flex flex-col lg:flex-row items-start gap-6">
        {/* Left Sidebar: Bidders & Trigger */}
        <Sidebar
          bidders={bidders}
          bids={bids}
          selectedBidderId={selectedBidderId}
          selectedBidSummary={selectedBidSummary}
          onSelectBidder={(id) => setSelectedBidderId(id)}
          onRunVerification={handleRunVerification}
          isVerifying={isVerifying}
          isLoading={isBiddersLoading}
        />

        {/* Center / Right Content Panel */}
        <main className="flex-1 w-full flex flex-col gap-6 min-w-0">
          {/* Stage Progression Bar */}
          <StageProgress run={currentRun} isVerifying={isVerifying} />

          {/* Compliance Checklist */}
          <ChecksList checks={checks} isLoading={isDetailsLoading} />

          {/* Submitted Documents & Extracted Facts */}
          {currentBid && (
            <DocumentList
              documents={documents}
              bidId={currentBid.id}
              isLoading={isDetailsLoading}
              onRefresh={() => loadBidderDetails(selectedBidderId!)}
            />
          )}

          {/* Split Row: AI Assistant & Officer Decision */}
          {currentBid && currentBidder && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AIChatPanel bidId={currentBid.id} bidderName={currentBidder.name} />
              <DecisionPanel
                bidId={currentBid.id}
                onDecisionSubmitted={() => {
                  loadBiddersList();
                  loadBidderDetails(selectedBidderId!);
                }}
              />
            </div>
          )}

          {/* SHA-256 Chained Audit Trail */}
          <AuditTrail
            events={auditEvents}
            isLoading={isAuditLoading}
            onRefresh={handleRefreshAudit}
          />
        </main>
      </div>
    </div>
  );
};

export default App;
