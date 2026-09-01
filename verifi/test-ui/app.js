const API_BASE = "http://localhost:8000/api/v1";

let currentTender = null;
let bidders = [];
let bids = [];
let selectedBidder = null;
let selectedBid = null;
let currentRun = null;
let pollingInterval = null;

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
  await checkHealth();
  await loadTender();
  await loadBiddersAndBids();
  
  // Set up health check heartbeat
  setInterval(checkHealth, 10000);
});

// Check Health
async function checkHealth() {
  const statusEl = document.getElementById("backend-status");
  const statusText = document.getElementById("backend-status-text");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      statusEl.className = "status-indicator online";
      statusText.textContent = "Backend: Connected";
    } else {
      throw new Error();
    }
  } catch (err) {
    statusEl.className = "status-indicator offline";
    statusText.textContent = "Backend: Disconnected (Port 8000)";
  }
}

// Load Active Tender
async function loadTender() {
  try {
    const res = await fetch(`${API_BASE}/tenders`);
    if (res.ok) {
      const data = await res.json();
      if (data.length > 0) {
        currentTender = data[0];
        document.getElementById("tender-number").textContent = currentTender.tender_number;
        document.getElementById("tender-title").textContent = currentTender.title;
        document.getElementById("tender-category").textContent = currentTender.category;
        document.getElementById("tender-value").textContent = `Est. Value: ₹${(currentTender.estimated_value_inr / 10000000).toFixed(2)} Cr`;
      }
    }
  } catch (err) {
    console.error("Failed to load tender:", err);
  }
}

// Load Bidders and Bids
async function loadBiddersAndBids() {
  try {
    const [biddersRes, bidsRes] = await Promise.all([
      fetch(`${API_BASE}/bidders`),
      fetch(`${API_BASE}/bids`),
    ]);

    if (biddersRes.ok && bidsRes.ok) {
      bidders = await biddersRes.json();
      bids = await bidsRes.json();

      document.getElementById("bidders-count").textContent = bidders.length;
      renderBiddersList();

      if (bidders.length > 0 && !selectedBidder) {
        selectBidder(bidders[0].id);
      }
    }
  } catch (err) {
    console.error("Failed to load bidders:", err);
  }
}

// Render Bidders List
function renderBiddersList() {
  const container = document.getElementById("bidders-list");
  container.innerHTML = "";

  bidders.forEach((bidder) => {
    const bid = bids.find((b) => b.bidder_id === bidder.id);
    const card = document.createElement("div");
    card.className = `bidder-card ${selectedBidder && selectedBidder.id === bidder.id ? "active" : ""}`;
    card.id = `bidder-card-${bidder.id}`;
    card.onclick = () => selectBidder(bidder.id);

    const scoreText = bid && bid.latest_score !== null && bid.latest_score !== undefined ? `${bid.latest_score}%` : "Pending";
    const riskBadgeClass = getRiskBadgeClass(bid ? bid.latest_risk_level : null);

    card.innerHTML = `
      <div class="bidder-card-top">
        <div>
          <div class="bidder-name">${escapeHtml(bidder.name)}</div>
          <div class="bidder-id">${bidder.id}</div>
        </div>
      </div>
      <div class="bidder-card-bottom">
        <span class="bidder-score-tag">${scoreText}</span>
        <span class="badge ${riskBadgeClass}">${bid && bid.latest_risk_level ? bid.latest_risk_level : "NOT RUN"}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

// Select Bidder
async function selectBidder(bidderId) {
  selectedBidder = bidders.find((b) => b.id === bidderId);
  selectedBid = bids.find((b) => b.bidder_id === bidderId);

  // Update UI active card
  document.querySelectorAll(".bidder-card").forEach((c) => c.classList.remove("active"));
  const activeCard = document.getElementById(`bidder-card-${bidderId}`);
  if (activeCard) activeCard.classList.add("active");

  // Update Summary Panel
  document.getElementById("detail-bidder-name").textContent = selectedBidder.name;
  document.getElementById("detail-bidder-id").textContent = `${selectedBidder.id} • Bid: ${selectedBid ? selectedBid.id : "N/A"}`;

  const scoreText = selectedBid && selectedBid.latest_score !== null && selectedBid.latest_score !== undefined ? `${selectedBid.latest_score}%` : "--%";
  const riskText = selectedBid && selectedBid.latest_risk_level ? selectedBid.latest_risk_level : "--";
  
  document.getElementById("detail-score").textContent = scoreText;
  const riskEl = document.getElementById("detail-risk");
  riskEl.textContent = riskText;
  riskEl.className = `metric-val ${getRiskColorClass(selectedBid ? selectedBid.latest_risk_level : null)}`;

  // Attach button click
  const runBtn = document.getElementById("btn-run-verification");
  runBtn.onclick = () => triggerVerification(selectedBid.id);

  // Clear or load current run
  if (selectedBid && selectedBid.latest_verification_run_id) {
    await fetchVerificationRun(selectedBid.latest_verification_run_id);
  } else {
    resetPipelineView();
  }

  // Load documents
  if (selectedBid) {
    await loadBidDocuments(selectedBid.id);
    await refreshAuditTrail();
    await loadDecision();
  }
}

// Trigger Verification
async function triggerVerification(bidId) {
  const runBtn = document.getElementById("btn-run-verification");
  runBtn.disabled = true;
  runBtn.innerHTML = "Starting pipeline...";

  try {
    const res = await fetch(`${API_BASE}/bids/${bidId}/verify`, { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      currentRun = data;
      document.getElementById("run-id-tag").textContent = `Run ID: ${data.run_id}`;
      
      // Start polling
      startPolling(data.run_id);
    } else {
      alert("Failed to start verification run.");
    }
  } catch (err) {
    console.error("Error starting verification:", err);
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> <span>RUN VERIFICATION PIPELINE</span>`;
  }
}

// Polling Pipeline Run
function startPolling(runId) {
  if (pollingInterval) clearInterval(pollingInterval);

  pollingInterval = setInterval(async () => {
    await fetchVerificationRun(runId);
    if (currentRun && (currentRun.status === "COMPLETED" || currentRun.status === "FAILED")) {
      clearInterval(pollingInterval);
      await loadBiddersAndBids(); // Refresh scores on bidder cards
      await refreshAuditTrail();
    }
  }, 400);
}

// Fetch Verification Run
async function fetchVerificationRun(runId) {
  try {
    const res = await fetch(`${API_BASE}/verification-runs/${runId}`);
    if (res.ok) {
      currentRun = await res.json();
      updatePipelineStages(currentRun);
      renderChecks(currentRun.checks);
      
      if (currentRun.score) {
        document.getElementById("detail-score").textContent = `${currentRun.score.total_score}%`;
      }
      if (currentRun.risk_assessment) {
        const riskEl = document.getElementById("detail-risk");
        riskEl.textContent = currentRun.risk_assessment.risk_level;
        riskEl.className = `metric-val ${getRiskColorClass(currentRun.risk_assessment.risk_level)}`;
      }
    }
  } catch (err) {
    console.error("Error fetching run:", err);
  }
}

// Update Pipeline Stages Bar
function updatePipelineStages(run) {
  document.getElementById("run-id-tag").textContent = `Run ID: ${run.id} • ${run.status}`;
  
  const stages = ["PENDING", "RUNNING", "OCR", "EXTRACTING", "VERIFYING", "RULE_EVALUATION", "SCORING", "AI_ANALYSIS", "COMPLETED"];
  const currentIdx = stages.indexOf(run.current_stage);

  stages.forEach((stage, idx) => {
    const el = document.querySelector(`.stage-item[data-stage="${stage}"]`);
    if (!el) return;

    if (idx < currentIdx || run.status === "COMPLETED") {
      el.className = "stage-item completed";
    } else if (idx === currentIdx) {
      el.className = "stage-item active";
    } else {
      el.className = "stage-item";
    }
  });

  const progressBar = document.getElementById("pipeline-progress-bar");
  progressBar.style.width = `${run.progress_pct || 0}%`;
}

// Render Checks Grid
function renderChecks(checks) {
  const container = document.getElementById("checks-container");
  if (!checks || checks.length === 0) {
    container.innerHTML = `<div class="empty-placeholder">Run verification to evaluate compliance rules against authoritative sources.</div>`;
    return;
  }

  container.innerHTML = "";
  checks.forEach((c) => {
    const card = document.createElement("div");
    card.className = "check-card";
    card.onclick = () => openCheckModal(c);

    const badgeClass = getStatusBadgeClass(c.status);

    card.innerHTML = `
      <div class="check-card-header">
        <span class="check-name">${escapeHtml(c.check_name)}</span>
        <span class="badge ${badgeClass}">${c.status}</span>
      </div>
      <div class="code-text">${c.rule_code} • ${c.document_type}</div>
      <div class="check-reason">${escapeHtml(c.reason)}</div>
    `;
    container.appendChild(card);
  });
}

// Open Check Details Modal
function openCheckModal(check) {
  const modal = document.getElementById("check-modal");
  document.getElementById("modal-check-title").textContent = `${check.check_name} (${check.rule_code})`;

  const modalBody = document.getElementById("modal-check-body");

  let discrepanciesHtml = "";
  if (check.fact_comparison && check.fact_comparison.discrepancies && check.fact_comparison.discrepancies.length > 0) {
    discrepanciesHtml = `
      <div style="background: #fee2e2; border: 1px solid #f87171; border-radius: 6px; padding: 10px; margin-bottom: 12px;">
        <strong style="color: #991b1b;">Discrepancies Detected:</strong>
        <ul style="margin-left: 20px; color: #7f1d1d; font-size: 12px;">
          ${check.fact_comparison.discrepancies.map((d) => `<li>${escapeHtml(d)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  modalBody.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <div>
        <strong>Status:</strong> <span class="badge ${getStatusBadgeClass(check.status)}">${check.status}</span>
      </div>
      <div class="code-text">Evaluated: ${new Date(check.evaluated_at).toLocaleTimeString()}</div>
    </div>
    
    ${discrepanciesHtml}

    <div style="margin-bottom: 12px;">
      <strong>Evaluation Reason:</strong>
      <p style="font-size: 13px; margin-top: 4px; color: #334155;">${escapeHtml(check.reason)}</p>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px;">
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px;">
        <strong style="font-size: 12px; color: #475569;">Extracted Document Facts:</strong>
        <pre style="font-size: 11px; margin-top: 6px; overflow-x: auto; background: #ffffff; padding: 8px; border: 1px solid #e2e8f0; border-radius: 4px;">${JSON.stringify(check.extracted_facts || {}, null, 2)}</pre>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px;">
        <strong style="font-size: 12px; color: #475569;">Authoritative Source Facts:</strong>
        <pre style="font-size: 11px; margin-top: 6px; overflow-x: auto; background: #ffffff; padding: 8px; border: 1px solid #e2e8f0; border-radius: 4px;">${JSON.stringify(check.source_facts || {}, null, 2)}</pre>
      </div>
    </div>
  `;

  modal.classList.remove("hidden");
}

function closeCheckModal() {
  document.getElementById("check-modal").classList.add("hidden");
}

// Load Bid Documents
async function loadBidDocuments(bidId) {
  const container = document.getElementById("documents-container");
  try {
    const res = await fetch(`${API_BASE}/bids/${bidId}/documents`);
    if (res.ok) {
      const docs = await res.json();
      if (docs.length === 0) {
        container.innerHTML = `<div class="empty-placeholder">No documents uploaded for this bid.</div>`;
        return;
      }

      container.innerHTML = "";
      docs.forEach((d) => {
        const item = document.createElement("div");
        item.className = "doc-item";
        item.innerHTML = `
          <div class="doc-info">
            <span class="doc-icon">📄</span>
            <div>
              <div class="doc-title">${escapeHtml(d.file_name)}</div>
              <div class="code-text">${d.document_type} • ${(d.file_size_bytes / 1024).toFixed(1)} KB • ${d.status}</div>
            </div>
          </div>
          <span class="doc-facts-tag">${Object.keys(d.extracted_facts || {}).length} facts extracted</span>
        `;
        container.appendChild(item);
      });
    }
  } catch (err) {
    console.error("Error loading documents:", err);
  }
}

// AI Assistant Chat
async function sendChatMessage() {
  const input = document.getElementById("ai-input");
  const message = input.value.trim();
  if (!message || !selectedBid) return;

  input.value = "";
  appendChatMessage(message, "user");

  try {
    const res = await fetch(`${API_BASE}/bids/${selectedBid.id}/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message }),
    });

    if (res.ok) {
      const data = await res.json();
      appendChatMessage(data.answer, "ai");
    } else {
      appendChatMessage("Error querying AI assistant.", "ai");
    }
  } catch (err) {
    appendChatMessage("Network error contacting AI service.", "ai");
  }
}

function sendQuickPrompt(promptText) {
  document.getElementById("ai-input").value = promptText;
  sendChatMessage();
}

function appendChatMessage(text, sender) {
  const history = document.getElementById("ai-chat-history");
  const msg = document.createElement("div");
  msg.className = `chat-message ${sender}-message`;
  msg.innerHTML = sender === "ai" ? `<strong>AI Assistant:</strong> ${escapeHtml(text)}` : escapeHtml(text);
  history.appendChild(msg);
  history.scrollTop = history.scrollHeight;
}

// Auto Draft Decision Reason
async function generateDecisionReason() {
  if (!selectedBid) return;
  const btn = document.getElementById("btn-generate-reason");
  btn.disabled = true;
  btn.textContent = "Drafting...";

  try {
    const res = await fetch(`${API_BASE}/bids/${selectedBid.id}/ai/generate-reason`, {
      method: "POST",
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("decision-reason").value = data.reason;
    } else {
      alert("Please run verification first before generating rationale.");
    }
  } catch (err) {
    console.error("Error generating reason:", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Auto-Draft Rationale";
  }
}

// Submit Decision
async function submitDecision(decisionType) {
  if (!selectedBid) return;
  const reason = document.getElementById("decision-reason").value.trim();
  if (!reason || reason.length < 5) {
    alert("Please enter a mandatory justification reason before submitting decision.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/bids/${selectedBid.id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision: decisionType,
        reason: reason,
        officer_id: "OFFICER-001",
        officer_name: "Senior Evaluation Officer",
      }),
    });

    if (res.ok) {
      const decision = await res.json();
      showDecisionAlert(decision);
      await refreshAuditTrail();
      await loadBiddersAndBids();
    } else {
      const err = await res.json();
      alert(`Decision error: ${err.error ? err.error.message : "Failed to record decision."}`);
    }
  } catch (err) {
    console.error("Error submitting decision:", err);
  }
}

async function loadDecision() {
  if (!selectedBid) return;
  try {
    const res = await fetch(`${API_BASE}/bids/${selectedBid.id}/decision`);
    if (res.ok) {
      const data = await res.json();
      if (data.current_decision) {
        showDecisionAlert(data.current_decision);
        document.getElementById("decision-reason").value = data.current_decision.reason;
      } else {
        hideDecisionAlert();
      }
    }
  } catch (err) {
    console.error("Error loading decision:", err);
  }
}

function showDecisionAlert(decision) {
  const alertEl = document.getElementById("decision-result-status");
  alertEl.classList.remove("hidden");
  if (decision.decision === "ACCEPTED") {
    alertEl.style.background = "#dcfce7";
    alertEl.style.color = "#15803d";
    alertEl.style.border = "1px solid #86efac";
    alertEl.innerHTML = `✓ <strong>OFFICER DECISION RECORDED: ACCEPTED</strong> by ${escapeHtml(decision.officer_name)} at ${new Date(decision.created_at).toLocaleTimeString()}`;
  } else {
    alertEl.style.background = "#fee2e2";
    alertEl.style.color = "#b91c1c";
    alertEl.style.border = "1px solid #fca5a5";
    alertEl.innerHTML = `✗ <strong>OFFICER DECISION RECORDED: REJECTED</strong> by ${escapeHtml(decision.officer_name)} at ${new Date(decision.created_at).toLocaleTimeString()}`;
  }
}

function hideDecisionAlert() {
  const alertEl = document.getElementById("decision-result-status");
  alertEl.classList.add("hidden");
  document.getElementById("decision-reason").value = "";
}

// Refresh Audit Trail
async function refreshAuditTrail() {
  if (!selectedBid) return;
  const container = document.getElementById("audit-trail-container");
  try {
    const res = await fetch(`${API_BASE}/bids/${selectedBid.id}/audit`);
    if (res.ok) {
      const events = await res.json();
      if (events.length === 0) {
        container.innerHTML = `<div class="empty-placeholder">No audit events logged yet.</div>`;
        return;
      }

      container.innerHTML = "";
      events.reverse().forEach((e) => {
        const item = document.createElement("div");
        item.className = "audit-item";
        item.innerHTML = `
          <div>
            <span class="audit-action">${e.action}</span>
            <div class="code-text">${e.actor} • ${new Date(e.timestamp).toLocaleTimeString()}</div>
          </div>
          <div class="audit-hash">
            SHA256: ${e.event_hash ? e.event_hash.substring(0, 16) : "-"}...
          </div>
        `;
        container.appendChild(item);
      });
    }
  } catch (err) {
    console.error("Error loading audit trail:", err);
  }
}

// Reset Pipeline View
function resetPipelineView() {
  document.getElementById("run-id-tag").textContent = "Run ID: -";
  document.querySelectorAll(".stage-item").forEach((s) => (s.className = "stage-item"));
  document.getElementById("pipeline-progress-bar").style.width = "0%";
  document.getElementById("checks-container").innerHTML = `<div class="empty-placeholder">Run verification to evaluate compliance rules against authoritative sources.</div>`;
  hideDecisionAlert();
}

// Helpers
function getStatusBadgeClass(status) {
  switch (status) {
    case "PASS": return "badge-pass";
    case "FAIL": return "badge-fail";
    case "REVIEW": return "badge-review";
    default: return "badge-na";
  }
}

function getRiskBadgeClass(risk) {
  switch (risk) {
    case "LOW": return "badge-low";
    case "MEDIUM": return "badge-medium";
    case "HIGH": return "badge-high";
    default: return "badge-na";
  }
}

function getRiskColorClass(risk) {
  switch (risk) {
    case "LOW": return "text-success";
    case "MEDIUM": return "text-warning";
    case "HIGH": return "text-danger";
    default: return "";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
