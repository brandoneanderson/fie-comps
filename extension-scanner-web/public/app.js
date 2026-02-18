// new integrated UI design with automated process
const scanButton = document.getElementById("scanButton");
const extensionUrlInput = document.getElementById("extensionUrl");
const resultsLink = document.getElementById("resultsLink");
const statusText = document.getElementById("statusText");

// Optional debug area (remove if you deleted it from HTML)
const debugOut = document.getElementById("debugOut");

// Results UI
const resultsPanel = document.getElementById("resultsPanel");
const resultsSummary = document.getElementById("resultsSummary");
const resultsJson = document.getElementById("resultsJson");

const toggleDetailsBtn = document.getElementById("toggleDetailsBtn");

const htmlReport = document.getElementById("htmlReport");

function $(id) {
  return document.getElementById(id);
}

function setTab(name) {
  document.querySelectorAll(".tab").forEach(t =>
    t.classList.toggle("active", t.dataset.tab === name)
  );
  document.querySelectorAll(".tab-panel").forEach(p =>
    p.classList.toggle("active", p.id === `tab-${name}`)
  );
}

document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => setTab(btn.dataset.tab));
});


function setStatus(msg) {
  if (statusText) statusText.textContent = msg;
}

function setDebug(obj) {
  if (!debugOut) return;
  debugOut.textContent = obj ? JSON.stringify(obj, null, 2) : "";
}

// Optional: unwrap Google redirect URLs from CSE
function normalizeStoreUrl(input) {
  try {
    const u = new URL(input);
    if (u.hostname === "www.google.com" && u.pathname === "/url") {
      const q = u.searchParams.get("q");
      if (q) return q;
    }
  } catch {
    // ignore invalid URLs
  }
  return input;
}

// If user types/pastes extension ID or URL, produce a canonical store URL for scanning
function coerceToWebStoreUrl(value) {
  const v = value.trim();
  if (!v) return v;
  const lower = v.toLowerCase();
  // Chrome extension IDs are 32 chars, [a-p]; accept exact ID or extract ID from text
  const exactId = lower.match(/^[a-p]{32}$/);
  const embeddedId = lower.match(/[a-p]{32}/);
  const id = exactId ? exactId[0] : (embeddedId ? embeddedId[0] : null);
  if (id) {
    return `https://chromewebstore.google.com/detail/${id}/${id}`;
  }
  // Already a URL (or Google redirect handled by normalizeStoreUrl)
  return v;
}

// Extract Chrome extension ID (32 chars [a-p]) from store URL or return null
function getExtensionIdFromStoreUrl(url) {
  if (!url || typeof url !== "string") return null;
  const m = url.toLowerCase().match(/[a-p]{32}/);
  return m ? m[0] : null;
}

// Format risk level for display (LOW -> "Low risk", etc.)
function formatRiskLevel(level) {
  if (!level) return "Unknown";
  const s = String(level).toUpperCase();
  const labels = { LOW: "Low risk", MEDIUM: "Medium risk", HIGH: "High risk", CRITICAL: "Critical risk" };
  return labels[s] || level;
}

// Build summary tab HTML from analysis + optional dataset metadata
function buildSummaryHtml(analysis, metadata) {
  const pred = analysis.prediction || {};
  const score = pred.risk_score != null ? Number(pred.risk_score) : null;
  const level = pred.risk_level || "";
  const action = pred.action || "";
  const name = metadata?.name || analysis.extension_name || "Unknown extension";
  const ratingValue = metadata?.ratingValue != null ? Number(metadata.ratingValue).toFixed(1) : null;
  const ratingCount = metadata?.ratingCount != null ? Number(metadata.ratingCount).toLocaleString() : null;

  let scoreClass = "summary-risk-low";
  if (level === "HIGH" || level === "CRITICAL") scoreClass = "summary-risk-high";
  else if (level === "MEDIUM") scoreClass = "summary-risk-medium";

  const scoreHtml = score != null
    ? `<div class="summary-score-wrap"><span class="summary-score ${scoreClass}">${score}</span><span class="summary-score-label">Risk score</span></div>`
    : "";

  const levelHtml = level
    ? `<div class="summary-level summary-level-${level.toLowerCase()}">${formatRiskLevel(level)}</div>`
    : "";

  const metaParts = [];
  metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Extension</span><span class="summary-meta-value">${escapeHtml(name)}</span></div>`);
  if (ratingValue != null && ratingCount != null) {
    metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Rating</span><span class="summary-meta-value">${escapeHtml(ratingValue)} ★ · ${escapeHtml(ratingCount)} ratings</span></div>`);
  } else if (ratingCount != null) {
    metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Ratings</span><span class="summary-meta-value">${escapeHtml(ratingCount)}</span></div>`);
  }
  if (action) {
    metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Recommendation</span><span class="summary-meta-value">${escapeHtml(action)}</span></div>`);
  }

  return `
    <div class="summary-cards">
      ${scoreHtml}
      ${levelHtml}
    </div>
    <div class="summary-meta">${metaParts.join("")}</div>
  `;
}

function escapeHtml(s) {
  if (s == null) return "";
  const div = document.createElement("div");
  div.textContent = String(s);
  return div.innerHTML;
}

function showResults(vm, extensionId) {
  if (!resultsPanel) return;
  resultsPanel.style.display = "block";

  // Support both nested (sample) and flat (real VM) response
  const analysis = vm?.analysis?.report ?? vm;
  if (!analysis || typeof analysis !== "object") {
    $("tab-summary").innerHTML = "<p class=\"summary-empty\">No analysis report returned.</p>";
    return;
  }

  // SUMMARY TAB: show loading then fill with risk score, level, metadata
  const summaryEl = $("tab-summary");
  summaryEl.innerHTML = "<p class=\"summary-loading\">Loading summary…</p>";

  (async () => {
    let metadata = null;
    if (extensionId) {
      try {
        const r = await fetch(`/api/extension/${encodeURIComponent(extensionId)}`);
        if (r.ok) metadata = await r.json();
      } catch {
        // ignore
      }
    }
    summaryEl.innerHTML = buildSummaryHtml(analysis, metadata);
  })();

  // MANIFEST TAB
  $("tab-manifest").textContent = JSON.stringify({
    permissions: analysis.permissions,
    host_permissions: analysis.host_permissions,
    security_policy: analysis.security_policy,
  }, null, 2);

  // HTML TAB
  $("tab-html").textContent =
    analysis.html_report ||
    JSON.stringify({
      features: analysis.html_features,
      examples: analysis.html_examples,
    }, null, 2);

  // CSS TAB
  //$("tab-css").textContent = JSON.stringify(analysis.css_features || {}, null, 2);
  $("tab-css").textContent = JSON.stringify({
    features: analysis.css_features || {},
    examples: analysis.css_examples || {}
  }, null, 2);

  // JS TAB
  // $("tab-js").textContent = JSON.stringify(analysis.js_features || {}, null, 2);
// JS TAB
  $("tab-js").textContent = JSON.stringify({
    features: analysis.js_features || {},
    examples: analysis.js_examples || {},
    totals: analysis.js_totals || null
  }, null, 2);

  // Default tab
  setTab("summary");
}

// ========== TEMPORARY_SAMPLE_RESULTS: delete from here through the showSampleResultsBtn listener (see index.html + styles.css) ==========
// Mock VM payload for previewing results without a running VM
function getSampleResultsVm() {
  return {
    analysis: {
      report: {
        extension_name: "Sample Extension (Test Data)",
        prediction: {
          label: "BENIGN",
          risk_score: 12,
          risk_level: "LOW",
          action: "Allow",
          confidence: "HIGH"
        },
        permissions: [
          "storage",
          "activeTab",
          "https://example.com/*"
        ],
        host_permissions: [
          "https://*.example.com/*",
          "https://api.example.com/*"
        ],
        security_policy: {
          content_security_policy: "script-src 'self'; object-src 'self'",
          sandbox: null
        },
        html_features: {
          script_tags: 3,
          iframe_count: 0,
          form_count: 1,
          external_links: 2
        },
        html_examples: [
          { tag: "script", src: "popup.js", inline: false },
          { tag: "a", href: "https://example.com/help" }
        ],
        html_report: null,
        css_features: {
          external_stylesheets: 1,
          inline_styles: 2,
          url_fetches: ["https://fonts.googleapis.com/css?family=Roboto"]
        },
        css_examples: [
          { rule: "@import", value: "url('theme.css')" },
          { property: "background", value: "linear-gradient(...)" }
        ],
        js_features: {
          eval_usage: false,
          dom_access: true,
          network_requests: ["fetch", "XMLHttpRequest"],
          storage_access: ["chrome.storage.local", "localStorage"]
        },
        js_examples: [
          { pattern: "chrome.tabs.query", file: "background.js", line: 42 },
          { pattern: "eval(", file: null, line: null }
        ],
        js_totals: {
          files_analyzed: 5,
          total_lines: 1200,
          api_calls: 18
        }
      }
    }
  };
}

function showSampleResults() {
  if (resultsLink) resultsLink.style.display = "inline-flex";
  setStatus("Sample results (no scan performed)");
  setDebug(null);
  showResults(getSampleResultsVm(), null);
}

async function runScan() {
  const raw = (extensionUrlInput?.value || "").trim();
  let url = normalizeStoreUrl(raw);
  url = coerceToWebStoreUrl(url);

  if (!url) {
    alert("Please enter a Chrome Web Store URL (or extension ID).");
    return;
  }

  try {
    setStatus("Submitting…");
    setDebug(null);
    if (resultsPanel) resultsPanel.style.display = "none";
    if (scanButton) scanButton.disabled = true;

    const r = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ store_url: url }),
    });

    // Parse response safely
    let data = null;
    try {
      data = await r.json();
      console.log("API response:", data);

    } catch {
      const t = await r.text();
      data = { ok: false, detail: "Non-JSON response from server", raw: t };
    }

    // If backend errored
    if (!r.ok || !data.ok) {
      setStatus("Error");
      console.error("Download failed:", r.status, data);
      setDebug({ http_status: r.status, request_url: url, response: data });
      return;
    }

    // Success
    setStatus("Downloaded successfully ✓");
    if (resultsLink) resultsLink.style.display = "inline-flex";

    const extensionId = getExtensionIdFromStoreUrl(url);
    showResults(data.vm, extensionId);

  } catch (e) {
    console.error("Network error:", e);
    setStatus("Network error");
    setDebug({ error: String(e) });
  } finally {
    if (scanButton) scanButton.disabled = false;
  }
}

// Toggle results panel when clicking the link 
if (resultsLink && resultsPanel) {
  resultsLink.addEventListener("click", () => {
    resultsPanel.style.display = (resultsPanel.style.display === "none") ? "block" : "none";
  });
}
  // if (toggleDetailsBtn && resultsJson) {
  //   toggleDetailsBtn.addEventListener("click", () => {
  //     const isHidden = resultsJson.style.display === "none" || !resultsJson.style.display;
  //     resultsJson.style.display = isHidden ? "block" : "none";
  //     toggleDetailsBtn.textContent = isHidden ? "Hide details" : "Show details";
  //   });
  // }


if (scanButton && extensionUrlInput) {
  scanButton.addEventListener("click", runScan);
  extensionUrlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runScan();
  });
}

const showSampleResultsBtn = document.getElementById("showSampleResults");
if (showSampleResultsBtn) {
  showSampleResultsBtn.addEventListener("click", showSampleResults);
}
// ========== /TEMPORARY_SAMPLE_RESULTS ==========

// --- Chrome Web Store search (dataset: extensions_clean.json) ---
(function () {
  function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }
  function toMessage(v) {
    if (v == null) return "Search failed";
    if (typeof v === "string") return v;
    if (typeof v === "object" && v.message) return String(v.message);
    return JSON.stringify(v);
  }

  const storeSearchResults = document.getElementById("storeSearchResults");
  if (!storeSearchResults || !extensionUrlInput) return;

  let debounceTimer = null;
  let lastQuery = "";

  function hideResults() {
    storeSearchResults.hidden = true;
    storeSearchResults.innerHTML = "";
  }

  function showResults(items) {
    storeSearchResults.innerHTML = "";
    if (!items.length) {
      storeSearchResults.hidden = true;
      return;
    }
    storeSearchResults.hidden = false;
    items.forEach((item) => {
      const option = document.createElement("div");
      option.className = "store-search-result-item";
      option.setAttribute("role", "option");
      option.tabIndex = 0;
      const icon = document.createElement("img");
      icon.className = "store-search-result-icon";
      icon.alt = "";
      icon.src = item.iconUrl || "";
      icon.onerror = () => {
        icon.style.display = "none";
        icon.nextElementSibling?.classList.add("store-search-result-icon-visible");
      };
      const placeholder = document.createElement("span");
      placeholder.className = "store-search-result-icon-placeholder";
      if (!item.iconUrl) placeholder.classList.add("store-search-result-icon-visible");
      placeholder.setAttribute("aria-hidden", "true");
      const textWrap = document.createElement("div");
      textWrap.className = "store-search-result-text";
      const text = document.createElement("span");
      text.className = "store-search-result-title";
      text.textContent = item.title || item.link || "Extension";
      const meta = document.createElement("div");
      meta.className = "store-search-result-meta";
      const idPart = item.extensionId ? `ID: ${item.extensionId}` : "";
      const ratingPart = item.ratingValue != null ? `${Number(item.ratingValue).toFixed(1)} ★` : "";
      const countPart = item.ratingCount != null ? `${Number(item.ratingCount).toLocaleString()} ratings` : "";
      meta.textContent = [idPart, ratingPart, countPart].filter(Boolean).join(" · ");
      textWrap.appendChild(text);
      textWrap.appendChild(meta);
      option.appendChild(icon);
      option.appendChild(placeholder);
      option.appendChild(textWrap);
      option.addEventListener("click", () => {
        extensionUrlInput.value = item.link;
        hideResults();
      });
      option.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          option.click();
        }
      });
      storeSearchResults.appendChild(option);
    });
  }

  extensionUrlInput.addEventListener("input", () => {
    const q = extensionUrlInput.value.trim();
    clearTimeout(debounceTimer);
    if (!q) {
      hideResults();
      return;
    }
    debounceTimer = setTimeout(async () => {
      lastQuery = q;
      try {
        const r = await fetch(`/api/store-search?q=${encodeURIComponent(q)}`);
        let data;
        try {
          data = await r.json();
        } catch {
          data = { detail: "Invalid response from server" };
        }
        if (r.status === 503) {
          storeSearchResults.hidden = false;
          storeSearchResults.innerHTML = `<div class="store-search-result-message">${escapeHtml(toMessage(data.detail || data.error))}</div>`;
          return;
        }
        if (!r.ok) {
          const msg = toMessage(data.detail || data.error || "Search failed");
          storeSearchResults.hidden = false;
          storeSearchResults.innerHTML = `<div class="store-search-result-message">${escapeHtml(msg)}</div>`;
          return;
        }
        if (lastQuery !== extensionUrlInput.value.trim()) return;
        showResults(data.items || []);
      } catch (e) {
        if (lastQuery !== extensionUrlInput.value.trim()) return;
        storeSearchResults.hidden = false;
        const msg = e?.message ? escapeHtml(e.message) : "Search failed. Try again.";
        storeSearchResults.innerHTML = `<div class="store-search-result-message">${msg}</div>`;
      }
    }, 280);
  });

  extensionUrlInput.addEventListener("focus", () => {
    if (storeSearchResults.children.length) storeSearchResults.hidden = false;
  });

  extensionUrlInput.addEventListener("blur", () => {
    setTimeout(hideResults, 180);
  });

  document.addEventListener("click", (e) => {
    if (!extensionUrlInput.closest(".store-search-wrap")?.contains(e.target)) {
      hideResults();
    }
  });
})();
