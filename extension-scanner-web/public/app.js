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

//I added this
const mlMoreButton = document.getElementById("mlMoreButton");
if (mlMoreButton) {
  mlMoreButton.addEventListener("click", () => {
    window.location.href = "/ml.html";
  });
}


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
  const labels = { SAFE: "Safe", LOW: "Low risk", MEDIUM: "Medium risk", HIGH: "High risk", CRITICAL: "Critical risk" };
  return labels[s] || level;
}

// Scoring guide thresholds from scoring.py (root) risk_level() – order: SAFE → CRITICAL
const SCORING_GUIDE = [
  { level: "SAFE", min: 0, max: 19 },
  { level: "LOW", min: 20, max: 29 },
  { level: "MEDIUM", min: 30, max: 49 },
  { level: "HIGH", min: 50, max: 79 },
  { level: "CRITICAL", min: 80, max: 100 },
];

function buildScoringGuideHtml() {
  const rows = SCORING_GUIDE.map(
    (r) => `<tr class="summary-guide-row summary-guide-${r.level.toLowerCase()}"><td>${escapeHtml(formatRiskLevel(r.level))}</td><td>${r.min} – ${r.max}</td></tr>`
  ).join("");
  return `
    <div class="summary-guide">
      <h4 class="summary-guide-title">Scoring guide</h4>
      <table class="summary-guide-table">
        <thead><tr><th>Risk level</th><th>Score range</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

// Build summary tab HTML from analysis + optional dataset metadata
function buildSummaryHtml(analysis, metadata) {
  const pred = analysis.prediction || {};
  const score = pred.risk_score != null ? Number(pred.risk_score) : null;
  const level = pred.risk_level || "";
  const action = pred.action || "";
  const name = metadata?.name || analysis.extension_name || "Unknown extension";
  // Rating from dataset (metadata) or from analysis report if backend provides it
  const rawRatingValue = metadata?.ratingValue ?? analysis.ratingValue;
  const rawRatingCount = metadata?.ratingCount ?? analysis.ratingCount;
  const ratingValue = rawRatingValue != null ? Number(rawRatingValue).toFixed(1) : null;
  const ratingCount = rawRatingCount != null ? Number(rawRatingCount).toLocaleString() : null;

  let scoreClass = "summary-risk-low";
  if (level === "HIGH" || level === "CRITICAL") scoreClass = "summary-risk-high";
  else if (level === "MEDIUM") scoreClass = "summary-risk-medium";

  const scoreHtml = score != null
    ? `<div class="summary-score-wrap">
    <span class="summary-score ${scoreClass}">${score}</span>
    <span class="summary-score-label">Risk score</span>
    </div>`
    : "";

  const levelHtml = level
    ? `<div class="summary-level summary-level-${level.toLowerCase()}">${formatRiskLevel(level)}</div>`
    : "";

  const metaParts = [];
  metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Extension</span><span class="summary-meta-value">${escapeHtml(name)}</span></div>`);
  if (ratingValue != null || ratingCount != null) {
    const ratingParts = [];
    if (ratingValue != null) ratingParts.push(`${escapeHtml(ratingValue)} ★`);
    if (ratingCount != null) ratingParts.push(`${escapeHtml(ratingCount)} ratings`);
    metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Rating</span><span class="summary-meta-value">${ratingParts.join(" · ")}</span></div>`);
  }
  if (action) {
    metaParts.push(`<div class="summary-meta-row"><span class="summary-meta-label-recommendation ${scoreClass}">Recommendation</span><span class="summary-meta-value">${escapeHtml(action)}</span></div>`);
  }

  return `
    <div class="summary-layout">
      <div class="summary-left">
        <div class="summary-cards">
          ${scoreHtml}
          ${levelHtml}
        </div>
        <div class="summary-meta">${metaParts.join("")}</div>
      </div>
      <div class="summary-right">${buildScoringGuideHtml()}</div>
    </div>
  `;
}

function escapeHtml(s) {
  if (s == null) return "";
  const div = document.createElement("div");
  div.textContent = String(s);
  return div.innerHTML;
}

// Permission names -> description for Manifest tab (keys lowercase for lookup)
const PERMISSION_DESCRIPTIONS = {
  webrequest: "Allows an extension to analyse network traffic by intercepting, blocking, and modifying requests in the browser",
  webrequestblocking: "Allows an extension to analyse network traffic by intercepting, blocking, and modifying requests in the browser",
  tabs: "Used to communicate with Chrome's tabs system by creating, modifying, or rearranging tabs in the browser",
  storage: "Provides data storage for client-side data",
  notifications: "Used to display desktop notifications to the user",
  cookies: "Used to query and modify browser's cookies.",
  management: "Provides ways to manipulate other extensions that are installed in the browser",
  contextmenus: "Allows an extension to add additional objects such as images, hyperlinks, and pages to Chrome's context menu",
  contentmenus: "Allows an extension to add additional objects such as images, hyperlinks, and pages to Chrome's context menu"
};

function getPermissionDescription(permission) {
  if (!permission || typeof permission !== "string") return null;
  const key = permission.toLowerCase().replace(/[^a-z0-9]/g, "");
  return PERMISSION_DESCRIPTIONS[key] || null;
}

function buildManifestHtml(analysis) {
  const perms = Array.isArray(analysis.permissions) ? analysis.permissions : [];
  const hostPerms = Array.isArray(analysis.host_permissions) ? analysis.host_permissions : [];
  const securityPolicy = analysis.security_policy;

  const permissionBars = perms.map((p) => {
    const desc = getPermissionDescription(p);
    const descHtml = desc ? `<div class="manifest-permission-desc">${escapeHtml(desc)}</div>` : "";
    const riskyClass = desc ? " manifest-permission-risky" : "";
    return `<div class="manifest-permission-bar${riskyClass}" data-permission="${escapeHtml(String(p))}"><div class="manifest-permission-label">${escapeHtml(String(p))}</div>${descHtml}</div>`;
  });

  let html = "";
  if (permissionBars.length) {
    html += `<div class="manifest-section"><h4 class="manifest-section-title">Permissions</h4><div class="manifest-permission-list">${permissionBars.join("")}</div></div>`;
  }
  if (hostPerms.length) {
    const hostBars = hostPerms.map((p) => `<div class="manifest-permission-bar manifest-host"><div class="manifest-permission-label">${escapeHtml(String(p))}</div><div class="manifest-permission-desc">Host or URL pattern this extension can access.</div></div>`);
    html += `<div class="manifest-section"><h4 class="manifest-section-title">Host permissions</h4><div class="manifest-permission-list">${hostBars.join("")}</div></div>`;
  }
  const hasSecurityPolicy = securityPolicy === true ||
    (securityPolicy && typeof securityPolicy === "object" && Object.keys(securityPolicy).length > 0);
  const cspDesc = "Help prevent websites from inadvertently executing malicious content.";
  const cspClass = hasSecurityPolicy ? " manifest-csp-present" : " manifest-csp-absent";
  html += `<div class="manifest-section"><h4 class="manifest-section-title">Security policy</h4><div class="manifest-permission-list"><div class="manifest-permission-bar${cspClass}"><div class="manifest-permission-label">${hasSecurityPolicy ? "Present" : "Not present"}</div><div class="manifest-permission-desc">${escapeHtml(cspDesc)}</div></div></div></div>`;
  if (!html) html = "<p class=\"manifest-empty\">No manifest permissions or policy data.</p>";
  return html;
}

// HTML tab: feature key -> description (same bar + dropdown pattern as Manifest)
const HTML_FEATURE_DESCRIPTIONS = {
  num_object_tags: "Counts the number of object HTML tags. The tag places an object in a document and contains information for retrieving ActiveX controls that are known to be exploitable.",
  num_embed_tags: "Counts <embed> and <applet> tags.",
  num_applet_tags: "Counts <embed> and <applet> tags.",
  num_iframe_tags: "Counts <iframe> tags in extension HTML pages. Allows the introducing of another HTML page into the current webpage. Common in phishing attacks.",
  num_inline_event_handlers: "Counts inline onclick=, onload=, etc. Represents the number of tags that attackers can make use of to jeopardize the victims' browsers through an XSS attack.",
  num_javascript_urls: "Counts javascript: URLs in attributes.",
  num_data_urls: "Counts data: URLs in attributes.",
  num_external_script_src: "Counts remote script loading (<script src=\"https://...\">).",
  num_meta_refresh: "Counts <meta http-equiv=\"refresh\"> redirects.",
  num_external_iframe_src: "Counts <iframe src=\"https://...\"> (external embedded content).",
  num_form_tags: "Counts <form> elements. Might be inserted and has the potential to be abused by an attacker.",
  num_external_form_actions: "Counts forms submitting to external URLs.",
  num_password_inputs: "Counts <input type=\"password\"> fields.",
  num_script_tags: "Counts <script> tags.",
  num_http_urls: "Counts http: URLs in attributes (insecure transport).",
  num_external_urls: "Counts external (http/https) URLs in attributes.",
  num_script_src_attrs: "Counts script src attributes (local or external).",
};

function getHtmlFeatureDescription(key) {
  return HTML_FEATURE_DESCRIPTIONS[key] || null;
}

function buildHtmlTabHtml(analysis) {
  const features = analysis.html_features && typeof analysis.html_features === "object" ? analysis.html_features : {};
  const keys = Object.keys(features).sort();
  if (!keys.length) return "<p class=\"manifest-empty\">No HTML features data.</p>";

  const bars = keys.map((key) => {
    const value = features[key];
    const desc = getHtmlFeatureDescription(key);
    const descHtml = desc ? `<div class="manifest-permission-desc">${escapeHtml(desc)}</div>` : "";
    const label = `${key}: ${value}`;
    return `<div class="manifest-permission-bar"><div class="manifest-permission-label">${escapeHtml(label)}</div>${descHtml}</div>`;
  });

  return `<div class="manifest-section"><div class="manifest-permission-list">${bars.join("")}</div></div>`;
}

// CSS tab: feature key -> description (same bar + dropdown pattern)
const CSS_FEATURE_DESCRIPTIONS = {
  num_background_image: "Records how many background-image properties contained in a CSS file. Malicious images could be injected into background properties.",
  num_behavior: "Calculates the frequency that behaviour property appears in a CSS file. It is possible to inject malicious codes into stylesheets via the property.",
  num_import_rules: "Counting the number of @import rules in a CSS file is because attacks would be likely to occur when untrusted files are loaded by the method.",
  num_external_urls: "Counts url() references in CSS that load external resources.",
};

function getCssFeatureDescription(key) {
  return CSS_FEATURE_DESCRIPTIONS[key] || null;
}

function buildCssTabHtml(analysis) {
  const features = analysis.css_features && typeof analysis.css_features === "object" ? analysis.css_features : {};
  const keys = Object.keys(features).sort();
  if (!keys.length) return "<p class=\"manifest-empty\">No CSS features data.</p>";

  const bars = keys.map((key) => {
    const value = features[key];
    const desc = getCssFeatureDescription(key);
    const descHtml = desc ? `<div class="manifest-permission-desc">${escapeHtml(desc)}</div>` : "";
    const label = `${key}: ${value}`;
    return `<div class="manifest-permission-bar"><div class="manifest-permission-label">${escapeHtml(label)}</div>${descHtml}</div>`;
  });

  return `<div class="manifest-section"><div class="manifest-permission-list">${bars.join("")}</div></div>`;
}

// JS tab: feature key -> description (same bar + dropdown pattern)
const JS_FEATURE_DESCRIPTIONS = {
  "whitespace %": "Used to detect common characteristics of obfuscated and packed malicious JS scripts. Lower whitespace % hints at such scripts.",
  avg_line_length: "Used to detect common characteristics of obfuscated and packed malicious JS scripts. Longer line lengths hints at such scripts.",
  specific_characters: "Obfuscated strings use excessively specific characters such as \\, [, ], @, x, and u.",
  word_size: "Obfuscated strings often use excessively long string sizes.",
  string_entropy: "Checks distribution of used byte codes. Low entropy signals easy predictability for character sequence (aaaaaaa). High entropy signals low predictability (4f!a8Z9#vP2@qR) signaling obfuscation.",
  dynamic_code_gen_functions: "Enables developers to create code dynamically in the form of a string (e.g., eval, setTimeout, and setInterval).",
  DOM_change_sinks: "Methods allow data to get executed if it is written in the context of a page. Passing unsanitized data to these sinks would inevitably lead to drive-by-download or DOM-based XSS vulnerabilities.",
  DOM_operations: "DOM change methods allow data to get executed if written in the context of a page. Passing unsanitized data to these sinks can lead to drive-by-download or DOM-based XSS vulnerabilities.",
  event_handlers: "Inline event handlers can allow JS to be invoked when the specified event occurs leading to potential vulnerabilities.",
  HTTP_scripts: "Counts the number of external scripts that are loaded over HTTPS. Importing scripts in background pages over HTTPS is extremely easy to create vulnerabilities.",
  modification_callbacks: "To effectively implement man-in-the-middle attacks, malicious extensions could strip or modify the security-related HTTP request and response headers by using callbacks in webRequest API.",
  XMLHttpRequests: "Can be used by extensions to access the network and deploy network attacks such as SQL injection and drive-by-download.",
  keyword_density: "Calculates the percentage of times JavaScript keywords appear in JavaScript code segment compared with the total amount of words. Malicious JS scripts have lower rates of keywords such as this, if, and var.",
  event_handlers_density: "Inline event handlers can allow JS to be invoked when the specified event occurs leading to potential vulnerabilities.",
  modification_callbacks_density: "To effectively implement man-in-the-middle attacks, malicious extensions could strip or modify the security-related HTTP request and response headers by using callbacks in webRequest API.",
  XMLHttpRequests_density: "Can be used by extensions to access the network and deploy network attacks such as SQL injection and drive-by-download.",
  HTTP_scripts_density: "Counts the number of external scripts that are loaded over HTTPS. Importing scripts in background pages over HTTPS is extremely easy to create vulnerabilities.",
  DOM_operations_density: "DOM change methods allow data to get executed if written in the context of a page. Passing unsanitized data to these sinks can lead to drive-by-download or DOM-based XSS vulnerabilities.",
  DOM_change_sinks_density: "Methods allow data to get executed if it is written in the context of a page. Passing unsanitized data to these sinks would inevitably lead to drive-by-download or DOM-based XSS vulnerabilities.",
};

function getJsFeatureDescription(key) {
  return JS_FEATURE_DESCRIPTIONS[key] || null;
}

function buildJsTabHtml(analysis) {
  const features = analysis.js_features && typeof analysis.js_features === "object" ? analysis.js_features : {};
  const keys = Object.keys(features).sort();
  if (!keys.length) return "<p class=\"manifest-empty\">No JavaScript features data.</p>";

  const bars = keys.map((key) => {
    const value = features[key];
    const desc = getJsFeatureDescription(key);
    const descHtml = desc ? `<div class="manifest-permission-desc">${escapeHtml(desc)}</div>` : "";
    const label = `${key}: ${value}`;
    return `<div class="manifest-permission-bar"><div class="manifest-permission-label">${escapeHtml(label)}</div>${descHtml}</div>`;
  });

  return `<div class="manifest-section"><div class="manifest-permission-list">${bars.join("")}</div></div>`;
}

function buildMlTabHtml(analysis) {
  const pred = analysis.prediction || {};
  const label = (pred.label || "").toUpperCase();
  const isBenign = label === "BENIGN";
  const isMalicious = label === "MALICIOUS";
  const riskScore = pred.risk_score != null ? pred.risk_score : null;
  const riskLevel = pred.risk_level || "";
  const confidence = pred.confidence || "";
  const action = pred.action || "";

  let labelClass = "ml-label-unknown";
  let labelText = "No prediction";
  if (isBenign) {
    labelClass = "ml-label-benign";
    labelText = "Benign";
  } else if (isMalicious) {
    labelClass = "ml-label-malicious";
    labelText = "Malicious";
  }

  const parts = [];
  parts.push(`<div class="ml-prediction-card"><span class="ml-prediction-label ${labelClass}">${escapeHtml(labelText)}</span><span class="ml-prediction-sublabel">Machine learning prediction</span></div>`);
  if (riskScore != null) parts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Risk score</span><span class="summary-meta-value">${escapeHtml(String(riskScore))}</span></div>`);
  if (riskLevel) parts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Risk level</span><span class="summary-meta-value">${escapeHtml(riskLevel)}</span></div>`);
  if (confidence) parts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Confidence</span><span class="summary-meta-value">${escapeHtml(confidence)}</span></div>`);
  if (action) parts.push(`<div class="summary-meta-row"><span class="summary-meta-label">Recommendation</span><span class="summary-meta-value">${escapeHtml(action)}</span></div>`);
  // parts.push(`<p class="ml-learn-more-wrap"><a href="/ml-explanation.html" target="_blank" rel="noopener noreferrer" class="ml-learn-more">Learn more</a> about how we use machine learning to generate these predictions.</p>`);
  parts.push(`<p class="ml-learn-more-wrap"><a href="/ml.html" target="_blank" rel="noopener noreferrer" class="ml-learn-more">Learn more</a> about how we use machine learning to generate these predictions.</p>`);


  return `<div class="manifest-section"><div class="ml-tab-content">${parts.join("")}</div></div>`;
}

function showResults(vm, extensionId) {
  if (!resultsPanel) return;
  // Keep panel hidden until user clicks "Click to view results"
  resultsPanel.style.display = "none";

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

  // MANIFEST TAB: permission bars with click-to-expand descriptions
  const manifestEl = $("tab-manifest");
  manifestEl.innerHTML = buildManifestHtml(analysis);
  manifestEl.classList.add("manifest-tab");
  manifestEl.querySelectorAll(".manifest-permission-bar").forEach((bar) => {
    bar.addEventListener("click", () => {
      const desc = bar.querySelector(".manifest-permission-desc");
      if (!desc) return;
      bar.classList.toggle("expanded");
    });
  });

  // HTML TAB: feature bars with click-to-expand descriptions
  const htmlTabEl = $("tab-html");
  htmlTabEl.innerHTML = buildHtmlTabHtml(analysis);
  htmlTabEl.classList.add("manifest-tab");
  htmlTabEl.querySelectorAll(".manifest-permission-bar").forEach((bar) => {
    bar.addEventListener("click", () => {
      const desc = bar.querySelector(".manifest-permission-desc");
      if (!desc) return;
      bar.classList.toggle("expanded");
    });
  });

  // CSS TAB: feature bars with click-to-expand descriptions
  const cssTabEl = $("tab-css");
  cssTabEl.innerHTML = buildCssTabHtml(analysis);
  cssTabEl.classList.add("manifest-tab");
  cssTabEl.querySelectorAll(".manifest-permission-bar").forEach((bar) => {
    bar.addEventListener("click", () => {
      const desc = bar.querySelector(".manifest-permission-desc");
      if (!desc) return;
      bar.classList.toggle("expanded");
    });
  });

  // JS TAB: feature bars with click-to-expand descriptions
  const jsTabEl = $("tab-js");
  jsTabEl.innerHTML = buildJsTabHtml(analysis);
  jsTabEl.classList.add("manifest-tab");
  jsTabEl.querySelectorAll(".manifest-permission-bar").forEach((bar) => {
    bar.addEventListener("click", () => {
      const desc = bar.querySelector(".manifest-permission-desc");
      if (!desc) return;
      bar.classList.toggle("expanded");
    });
  });

  // ML PREDICTION TAB
  const mlTabEl = $("tab-ml");
  mlTabEl.innerHTML = buildMlTabHtml(analysis);
  mlTabEl.classList.add("manifest-tab");

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
        ratingValue: 4.4,
        ratingCount: 60989,
        prediction: {
          label: "BENIGN",
          risk_score: 21,
          risk_level: "LOW",
          action: "Allow",
          confidence: "HIGH"
        },
        permissions: [
          "storage",
          "tabs",
          "webrequest",
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
          num_background_image: 2,
          num_behavior: 0,
          num_import_rules: 1,
          num_external_urls: 3
        },
        css_examples: [
          { rule: "@import", value: "url('theme.css')" },
          { property: "background", value: "linear-gradient(...)" }
        ],
        js_features: {
          "whitespace %": 0.18,
          avg_line_length: 42,
          specific_characters: 0.02,
          word_size: 4.2,
          string_entropy: 3.1,
          dynamic_code_gen_functions: 2,
          DOM_change_sinks: 0,
          event_handlers: 1,
          HTTP_scripts: 0,
          modification_callbacks: 0,
          XMLHttpRequests: 1,
          keyword_density: 0.08
        },
        js_examples: [],
        js_totals: { file_count: 5, total_lines: 1200, total_chars: 45000 }
      }
    }
  };
}

function showSampleResults() {
  if (resultsLink) resultsLink.style.display = "inline-flex";
  setStatus("Sample results generated");
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
  }
);
})();
