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

// If user pastes extension ID, build a canonical URL
function coerceToWebStoreUrl(value) {
  const v = value.trim();
  // Chrome extension IDs are 32 chars, lowercase a-p
  if (/^[a-p]{32}$/.test(v)) {
    return `https://chromewebstore.google.com/detail/${v}/${v}`;
  }
  return v;
}


function showResults(vm) {
  if (!resultsPanel) return;
  resultsPanel.style.display = "block";

  const analysis = vm?.analysis?.report;
  if (!analysis) {
    $("tab-summary").textContent = "No analysis report returned.";
    return;
  }

  // SUMMARY TAB
  $("tab-summary").textContent =
    `Extension: ${analysis.extension_name}\n\n` +
    `Prediction: ${JSON.stringify(analysis.prediction, null, 2)}`;

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
  $("tab-css").textContent = JSON.stringify(analysis.css_features || {}, null, 2);

  // JS TAB
  $("tab-js").textContent = JSON.stringify(analysis.js_features || {}, null, 2);

  // Default tab
  setTab("summary");
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

    // Show analysis results from VM
    showResults(data.vm);

  } catch (e) {
    console.error("Network error:", e);
    setStatus("Network error");
    setDebug({ error: String(e) });
  } finally {
    if (scanButton) scanButton.disabled = false;
  }
}

// Toggle results panel when clicking the link (register ONCE)
if (resultsLink && resultsPanel) {
  resultsLink.addEventListener("click", () => {
    resultsPanel.style.display = (resultsPanel.style.display === "none") ? "block" : "none";
  });
}
  if (toggleDetailsBtn && resultsJson) {
    toggleDetailsBtn.addEventListener("click", () => {
      const isHidden = resultsJson.style.display === "none" || !resultsJson.style.display;
      resultsJson.style.display = isHidden ? "block" : "none";
      toggleDetailsBtn.textContent = isHidden ? "Hide details" : "Show details";
    });
  }


if (scanButton && extensionUrlInput) {
  scanButton.addEventListener("click", runScan);
  extensionUrlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runScan();
  });
}
