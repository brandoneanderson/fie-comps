// import express from "express";
// import path from "path";
// import { fileURLToPath } from "url";
// import { execFile } from "child_process";

// const app = express();
// app.use(express.json());

// // --- config ---
// const PORT = 3000;
// const VM_USER = "fiecomps";
// const VM_IP = "192.168.217.128";
// const VM_DOWNLOADER = "/home/fiecomps/vm_downloader.py";

// // --- static site ---
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);
// app.use(express.static(path.join(__dirname, "public")));

// // --- helpers ---
// function shellEscapeSingleQuotes(s) {
//   return `'${String(s).replace(/'/g, `'\\''`)}'`;
// }

// function runVmDownloaderOverSsh(store_url) {
//   return new Promise((resolve, reject) => {
//     const sshPath = "/usr/bin/ssh";
//     const safeUrl = shellEscapeSingleQuotes(store_url);

//     // Run a single remote command so special chars (like &) won't break
//     const remoteCmd = `python3 ${VM_DOWNLOADER} ${safeUrl}`;

//     execFile(
//       sshPath,
//       ["-4", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", `${VM_USER}@${VM_IP}`, remoteCmd],
//       { timeout: 120000 },
//       (err, stdout, stderr) => {
//         if (err) return reject(new Error((stderr || stdout || String(err)).trim()));
//         resolve(stdout.trim());
//       }
//     );
//   });
// }

// // --- routes ---
// app.post("/api/download", async (req, res) => {
//   try {
//     const { store_url } = req.body || {};
//     if (!store_url) return res.status(400).json({ detail: "Missing store_url" });

//     const outText = await runVmDownloaderOverSsh(store_url);
//     res.type("application/json").send(outText);
//   } catch (e) {
//     res.status(500).json({ detail: String(e) });
//   }
// });

// app.listen(PORT, () => {
//   console.log(`UI: http://localhost:${PORT}`);
// });

// NEW INTEGRATED DESIGN
import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { execFile } from "child_process";

const app = express();
app.use(express.json());

// --- config ---
const PORT = 3000;

const VM_USER = process.env.VM_USER || "fiecomps";
const VM_IP = process.env.VM_IP || "192.168.217.128";
const VM_DOWNLOADER = process.env.VM_DOWNLOADER || "/home/fiecomps/vm_downloader.py";

// If you want to force a specific SSH key file, set VM_SSH_KEY=/path/to/key
const VM_SSH_KEY = process.env.VM_SSH_KEY || "";

// --- static site ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, "public")));

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

    console.log("[ssh] cmd:", sshPath, args.join(" "));

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
  // try {
  //   const { store_url } = req.body || {};
  //   if (!store_url) return res.status(400).json({ detail: "Missing store_url" });

  //   const { stdout, stderr } = await runVmDownloaderOverSsh(store_url);

  //   // stdout should ideally be JSON; but don’t assume it is.
  //   // Return a JSON wrapper so frontend always gets structured data.
  //   let parsed = null;
  //   try {
  //     parsed = stdout ? JSON.parse(stdout) : null;
  //   } catch {
  //     parsed = null;
  //   }

  //   res.json({
  //     ok: true,
  //     store_url,
  //     parsed,        // if stdout was valid JSON
  //     raw_stdout: stdout,
  //     raw_stderr: stderr,
  //   });
  // } catch (e) {
  //   res.status(500).json({
  //     ok: false,
  //     detail: String(e?.message || e),
  //   });
  // }
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
