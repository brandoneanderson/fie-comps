
// const storeUrlEl = document.getElementById("storeUrl");
// const statusEl = document.getElementById("status");
// const statusPre = document.getElementById("statusPre");
// const btnEl = document.getElementById("downloadBtn");

// function setStatus(msg) {
//   statusEl.textContent = msg;
// }
// function setJson(obj) {
//   statusPre.textContent = obj ? JSON.stringify(obj, null, 2) : "";
// }

// // Optional: if user pastes a Google redirect URL from CSE, unwrap it
// function normalizeStoreUrl(input) {
//   try {
//     const u = new URL(input);
//     if (u.hostname === "www.google.com" && u.pathname === "/url") {
//       const q = u.searchParams.get("q");
//       if (q) return q;
//     }
//   } catch {}
//   return input;
// }

// btnEl.addEventListener("click", async () => {
//   const url = normalizeStoreUrl(storeUrlEl.value.trim());

//   setStatus("Submitting…");
//   setJson(null);

//   if (!url) return setStatus("Please paste a Chrome Web Store URL.");

//   try {
//     const r = await fetch("/api/download", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ store_url: url }),
//     });

//     const text = await r.text();
//     let data;
//     try {
//       data = JSON.parse(text);
//     } catch {
//       data = { raw: text };
//     }

//     if (!r.ok) {
//       setStatus(`Error (${r.status})`);
//       setJson(data);
//       return;
//     }

//     setStatus("Downloaded ✓");
//     setJson(data);
//   } catch (e) {
//     setStatus(`Network error: ${String(e)}`);
//   }
// });

//MERGED VERSION - WORKS
// const scanButton = document.getElementById("scanButton");
// const extensionUrlInput = document.getElementById("extensionUrl");
// const resultsLink = document.getElementById("resultsLink");
// const statusText = document.getElementById("statusText");
// const debugOut = document.getElementById("debugOut");


// function setStatus(msg) {
//   if (statusText) statusText.textContent = msg;
// }
// function setDebug(obj) {
//   if (!debugOut) return;
//   debugOut.textContent = obj ? JSON.stringify(obj, null, 2) : "";
// }

// // Optional: unwrap Google redirect URLs from CSE
// function normalizeStoreUrl(input) {
//   try {
//     const u = new URL(input);
//     if (u.hostname === "www.google.com" && u.pathname === "/url") {
//       const q = u.searchParams.get("q");
//       if (q) return q;
//     }
//   } catch {
//     // ignore invalid
//   }
//   return input;
// }

// // If user pastes extension ID, build a canonical URL
// function coerceToWebStoreUrl(value) {
//   const v = value.trim();
//   // extension ID pattern: 32 lowercase letters
//   if (/^[a-z]{32}$/.test(v)) {
//     return `https://chromewebstore.google.com/detail/${v}/${v}`;
//   }
//   return v;
// }

// async function runScan() {
//   const raw = (extensionUrlInput?.value || "").trim();
//   let url = normalizeStoreUrl(raw);
//   url = coerceToWebStoreUrl(url);

//   if (!url) {
//     alert("Please enter a Chrome Web Store URL (or extension ID).");
//     return;
//   }

//   try {
//     setStatus("Submitting…");
//     setDebug(null);
//     if (scanButton) scanButton.disabled = true;

//     const r = await fetch("/api/download", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ store_url: url }),
//     });

//     const data = await r.json().catch(async () => {
//       const t = await r.text();
//       return { ok: false, detail: "Non-JSON response from server", raw: t };
//     });

//     // setDebug({ http_status: r.status, request_url: url, response: data });

//     if (!r.ok || !data.ok) {
//       setStatus("Error — see details below");
//       console.error("Download failed:", r.status, data);
//       return;
//     }

//     setStatus("Downloaded ✓");

//     if (resultsLink) {
//       resultsLink.style.display = "inline-flex";
//       resultsLink.scrollIntoView({ behavior: "smooth", block: "center" });
//     }
//   } catch (e) {
//     console.error("Network error:", e);
//     setStatus("Network error");
//     setDebug({ error: String(e) });
//   } finally {
//     if (scanButton) scanButton.disabled = false;
//   }
// }

// if (scanButton && extensionUrlInput) {
//   scanButton.addEventListener("click", runScan);
//   extensionUrlInput.addEventListener("keydown", (e) => {
//     if (e.key === "Enter") runScan();
//   });
// }

//Merged with scan report
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
  if (resultsPanel) resultsPanel.style.display = "block";

  const analysis = vm?.analysis;

  if (analysis?.ok && analysis.report) {
    if (resultsSummary) resultsSummary.textContent = "Analysis completed successfully.";
    if (resultsJson) resultsJson.textContent = JSON.stringify(analysis.report, null, 2);
  } else {
    if (resultsSummary) resultsSummary.textContent = "Downloaded, but analysis failed.";
    if (resultsJson) resultsJson.textContent = JSON.stringify(analysis || { error: "No analysis output" }, null, 2);
  }
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

if (scanButton && extensionUrlInput) {
  scanButton.addEventListener("click", runScan);
  extensionUrlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runScan();
  });
}
