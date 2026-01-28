
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

// btnEl.addEventListener("click", async () => {
//   const url = storeUrlEl.value.trim();
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
//     try { data = JSON.parse(text); } catch { data = { raw: text }; }

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
const storeUrlEl = document.getElementById("storeUrl");
const statusEl = document.getElementById("status");
const statusPre = document.getElementById("statusPre");
const btnEl = document.getElementById("downloadBtn");

function setStatus(msg) {
  statusEl.textContent = msg;
}
function setJson(obj) {
  statusPre.textContent = obj ? JSON.stringify(obj, null, 2) : "";
}

// Optional: if user pastes a Google redirect URL from CSE, unwrap it
function normalizeStoreUrl(input) {
  try {
    const u = new URL(input);
    if (u.hostname === "www.google.com" && u.pathname === "/url") {
      const q = u.searchParams.get("q");
      if (q) return q;
    }
  } catch {}
  return input;
}

btnEl.addEventListener("click", async () => {
  const url = normalizeStoreUrl(storeUrlEl.value.trim());

  setStatus("Submitting…");
  setJson(null);

  if (!url) return setStatus("Please paste a Chrome Web Store URL.");

  try {
    const r = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ store_url: url }),
    });

    const text = await r.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }

    if (!r.ok) {
      setStatus(`Error (${r.status})`);
      setJson(data);
      return;
    }

    setStatus("Downloaded ✓");
    setJson(data);
  } catch (e) {
    setStatus(`Network error: ${String(e)}`);
  }
});
