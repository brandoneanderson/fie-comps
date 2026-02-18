// NEW INTEGRATED DESIGN
import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { execFile } from "child_process";
import fs from "fs";

const app = express();
app.use(express.json());

// --- config ---
const PORT = 3000;

const VM_USER = process.env.VM_USER || "fiecomps";
// const VM_IP = process.env.VM_IP || "192.168.217.128"; 
const VM_IP = process.env.VM_IP || "192.168.173.128"; 
const VM_DOWNLOADER = process.env.VM_DOWNLOADER || "/home/fiecomps/vm_downloader.py";

// If you want to force a specific SSH key file, set VM_SSH_KEY=/path/to/key
const VM_SSH_KEY = process.env.VM_SSH_KEY || "";

// --- static site ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, "public")));

// --- extensions dataset (lazy load and cache) ---
const EXTENSIONS_JSON_PATH = path.join(__dirname, "public", "extensions_clean.json");
const MAX_SEARCH_RESULTS = 20;
let extensionsLoadPromise = null;

function loadExtensions() {
  if (!extensionsLoadPromise) {
    extensionsLoadPromise = fs.promises
      .readFile(EXTENSIONS_JSON_PATH, "utf8")
      .then((raw) => {
        const list = JSON.parse(raw);
        console.log(`[store-search] Loaded ${list.length} extensions from dataset`);
        return list;
      })
      .catch((err) => {
        extensionsLoadPromise = null;
        throw err;
      });
  }
  return extensionsLoadPromise;
}

// Start loading dataset at startup (non-blocking)
loadExtensions().catch((err) => console.error("[store-search] Startup load failed:", err.message));

// Search extensions dataset by name; returns { items: [{ title, link, iconUrl, extensionId }] }
app.get("/api/store-search", async (req, res) => {
  const q = (req.query.q || "").trim();
  if (!q) return res.json({ items: [] });

  try {
    const list = await loadExtensions();
    const lower = q.toLowerCase();
    const items = list
      .filter(
        (ext) =>
          (ext.name && ext.name.toLowerCase().includes(lower)) ||
          (ext.id && ext.id.toLowerCase().includes(lower))
      )
      .slice(0, MAX_SEARCH_RESULTS)
      .map((ext) => ({
        title: ext.name || "",
        link: ext.url || `https://chromewebstore.google.com/detail/${ext.id || ""}`,
        iconUrl: ext.logo || null,
        extensionId: ext.id || null,
        ratingValue: ext.ratingValue != null ? ext.ratingValue : null,
        ratingCount: ext.ratingCount != null ? ext.ratingCount : null,
      }));
    res.json({ items });
  } catch (e) {
    console.error("[store-search] Error:", e);
    res.status(500).json({
      error: "Search failed",
      detail: e.code === "ENOENT" ? "Dataset not found (extensions_clean.json)." : String(e?.message || e),
    });
  }
});

// Get one extension by ID from dataset (for summary metadata)
app.get("/api/extension/:id", async (req, res) => {
  const id = (req.params.id || "").trim().toLowerCase();
  if (!id) return res.status(400).json({ error: "Missing extension id" });
  try {
    const list = await loadExtensions();
    const ext = list.find((e) => (e.id || "").toLowerCase() === id);
    if (!ext) return res.status(404).json({ error: "Extension not found", id });
    res.json(ext);
  } catch (e) {
    console.error("[extension] Error:", e);
    res.status(500).json({ error: "Lookup failed", detail: String(e?.message || e) });
  }
});

function shellEscapeSingleQuotes(s) {
  return `'${String(s).replace(/'/g, `'\\''`)}'`;
}

function runVmDownloaderOverSsh(store_url) {
  return new Promise((resolve, reject) => {
    const sshPath = "/usr/bin/ssh";
    const safeUrl = shellEscapeSingleQuotes(store_url);

    // Run a single remote command so special chars won't break
    const remoteCmd = `python3 ${VM_DOWNLOADER} ${safeUrl}`;

    const args = [
      "-4",
      "-o",
      "BatchMode=yes",
      "-o",
      "ConnectTimeout=10",
      "-o",
      "ServerAliveInterval=10",
      "-o",
      "ServerAliveCountMax=2",

      // Dev-friendly: avoids host key prompts breaking BatchMode
      "-o",
      "StrictHostKeyChecking=no",
      "-o",
      "UserKnownHostsFile=/dev/null",
    ];

    if (VM_SSH_KEY) {
      args.push("-i", VM_SSH_KEY);
    }

    args.push(`${VM_USER}@${VM_IP}`, remoteCmd);

    // console.log("[ssh] cmd:", sshPath, args.join(" "));
    if (process.env.DEBUG_SSH === "1") {
      console.log("[ssh] cmd:", sshPath, args.join(" "));
    }

    execFile(
      sshPath,
      args,
      { timeout: 120000 },
      (err, stdout, stderr) => {
        const out = (stdout || "").trim();
        const errOut = (stderr || "").trim();

        if (err) {
          // Reject with a useful message
          const msg = [
            "SSH/VM downloader failed.",
            errOut && `stderr: ${errOut}`,
            out && `stdout: ${out}`,
            `err: ${String(err)}`,
          ]
            .filter(Boolean)
            .join("\n");

          return reject(new Error(msg));
        }

        resolve({ stdout: out, stderr: errOut });
      }
    );
  });
}

app.post("/api/download", async (req, res) => {
  try {
    const { store_url } = req.body || {};
    if (!store_url) return res.status(400).json({ ok: false, detail: "Missing store_url" });

    const { stdout, stderr } = await runVmDownloaderOverSsh(store_url);

    let vm;
    try {
      vm = JSON.parse(stdout);
    } catch {
      return res.status(500).json({
        ok: false,
        detail: "VM did not return JSON",
        raw_stdout: stdout,
        raw_stderr: stderr,
      });
    }

    res.json({ ok: true, vm });
  } catch (e) {
    res.status(500).json({ ok: false, detail: String(e?.message || e) });
  }
});

app.listen(PORT, () => {
  console.log(`UI: http://localhost:${PORT}`);
});
