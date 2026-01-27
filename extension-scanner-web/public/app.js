
// const storeUrlEl = document.getElementById("storeUrl");
// const statusEl = document.getElementById("status");
// const btnEl = document.getElementById("downloadBtn");

// function setStatus(msg) {
//   statusEl.textContent = msg;
// }

// btnEl.addEventListener("click", async () => {
//   const url = storeUrlEl.value.trim();
//   setStatus("Submitting…");

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
//       return setStatus(`Error (${r.status}): ${data.detail || JSON.stringify(data, null, 2)}`);
//     }

//     setStatus(JSON.stringify(data, null, 2));
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

btnEl.addEventListener("click", async () => {
  const url = storeUrlEl.value.trim();
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
    try { data = JSON.parse(text); } catch { data = { raw: text }; }

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
