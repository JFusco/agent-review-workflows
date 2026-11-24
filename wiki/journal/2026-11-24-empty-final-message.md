---
topics: [writer-startup-recovery]
---

# Empty final-message receipt during writer startup

The Office timeline review exposed a Codex launch that created an empty output file before its app server failed. Repair recovery now hashes that file alongside the original call receipts. Nonempty messages, links and nonregular outputs still stop recovery. [Issue 113](https://github.com/JFusco/agent-review-workflows/issues/113)
