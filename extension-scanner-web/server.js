
import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import http from "http";

const app = express();
app.use(express.json());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Serve /public
app.use(express.static(path.join(__dirname, "public")));

const VM_HOST = "192.168.217.128";
const VM_PORT = 8000;

function postJsonToVm(pathname, payload) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload);

    const req = http.request(
      {
        host: VM_HOST,
        port: VM_PORT,
        path: pathname,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(data),
        },
        timeout: 120000,
      },
      (res) => {
        let body = "";
        res.setEncoding("utf8");
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => resolve({ status: res.statusCode || 500, body }));
      }
    );

    req.on("timeout", () => {
      req.destroy(new Error("VM request timed out"));
    });

    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

// Browser -> Mac -> VM
app.post("/api/download", async (req, res) => {
  try {
    const { store_url } = req.body || {};
    console.log("Browser requested:", store_url);

    if (!store_url) return res.status(400).json({ detail: "Missing store_url" });

    const out = await postJsonToVm("/download", { store_url });
    res.status(out.status).send(out.body);
  } catch (e) {
    console.error("Proxy error:", e);
    res.status(500).json({ detail: String(e) });
  }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`UI: http://localhost:${PORT}`));
