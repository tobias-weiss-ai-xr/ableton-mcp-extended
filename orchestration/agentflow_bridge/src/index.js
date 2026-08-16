#!/usr/bin/env node
/**
 * AgentFlow Bridge for Ableton MCP Extended
 *
 * Orchestrates the agentic mix workflow using AgentFlow's DAG engine,
 * circuit breakers, and checkpoint persistence. Python agents are
 * exposed via HTTP endpoints that this engine calls.
 *
 * Architecture:
 *   Node.js (this file) ←→ AgentFlow DAG engine
 *                          ←→ HTTP agent invoker → Python (localhost:AGENTFLOW_PORT)
 *
 * Workflow: configure → setup_session → generate_clips → construct_arrangement
 *           → [execute_section → analyze_section] (loop until done)
 *           → analyze_and_adapt
 *
 * REST API:
 *   POST /workflow/start     — start a mix workflow (JSON body = config)
 *   GET  /workflow/:id/status — get execution status
 *   POST /workflow/:id/cancel — cancel execution
 *   GET  /health             — health check
 */

import { WorkflowExecutionEngine } from "agentflow";
import { InMemoryCheckpointStore } from "agentflow";
import { CircuitBreakerRegistry } from "agentflow";
import { EventBus } from "agentflow";

// ── Config ───────────────────────────────────────────────────────────────────
const DEFAULT_PORT = parseInt(process.env.AGENTFLOW_PORT || "7420", 10);
const AGENT_PORT = parseInt(process.env.AGENT_PORT || "7421", 10);

// ── Ableton Mix Workflow Definition ────────────────────────────────────────────
// Mirrors the LangGraph pipeline in agentic_mix/graph.py
const abletonMixWorkflow = {
  id: "ableton-mix",
  name: "Ableton Agentic Mix",
  description: "AI-driven Ableton Live session generation with audio feedback loop",
  tasks: [
    {
      id: "configure",
      name: "Configure Mix",
      agentId: "python-agent",
      input: { action: "configure" },
      dependencies: [],
      strategy: "sequential",
      retryPolicy: { maxAttempts: 2, initialDelayMs: 2000, maxDelayMs: 15000, backoffMultiplier: 2 },
    },
    {
      id: "setup-session",
      name: "Setup Session",
      agentId: "python-agent",
      input: { action: "setup_session" },
      dependencies: ["configure"],
      strategy: "sequential",
      retryPolicy: { maxAttempts: 2, initialDelayMs: 2000, maxDelayMs: 15000, backoffMultiplier: 2 },
    },
    {
      id: "generate-clips",
      name: "Generate Clips",
      agentId: "python-agent",
      input: { action: "generate_clips" },
      dependencies: ["setup-session"],
      strategy: "sequential",
      retryPolicy: { maxAttempts: 3, initialDelayMs: 3000, maxDelayMs: 30000, backoffMultiplier: 2 },
    },
    {
      id: "construct-arrangement",
      name: "Construct Arrangement",
      agentId: "python-agent",
      input: { action: "construct_arrangement" },
      dependencies: ["generate-clips"],
      strategy: "sequential",
      retryPolicy: { maxAttempts: 2, initialDelayMs: 2000, maxDelayMs: 15000, backoffMultiplier: 2 },
    },
    {
      id: "execute-section-loop",
      name: "Section Execution Loop",
      agentId: "python-loop-agent",
      input: { action: "execute_section_loop" },
      dependencies: ["construct-arrangement"],
      strategy: "sequential",
      retryPolicy: { maxAttempts: 1, initialDelayMs: 1000, maxDelayMs: 5000, backoffMultiplier: 1 },
    },
    {
      id: "analyze-and-adapt",
      name: "Analyze and Adapt",
      agentId: "python-agent",
      input: { action: "analyze_and_adapt" },
      dependencies: ["execute-section-loop"],
      strategy: "sequential",
    },
  ],
  entryPoints: ["configure"],
  exitPoints: ["analyze-and-adapt"],
};

// ── In-memory task results for the section loop ─────────────────────────────
const taskResults = new Map();

// ── Event bus ─────────────────────────────────────────────────────────────────
const eventBus = new EventBus({ maxSubscriptions: 100 });
const circuitRegistry = new CircuitBreakerRegistry({
  defaultConfig: {
    failureThreshold: 3,
    recoveryTimeoutMs: 30000,
    halfOpenMaxCalls: 2,
  },
});

// ── Checkpoint store (file-based for durability) ───────────────────────────
const checkpointStore = new InMemoryCheckpointStore();

// ── Execution engine ──────────────────────────────────────────────────────────
const engine = new WorkflowExecutionEngine({
  circuitBreakerRegistry: circuitRegistry,
  checkpointStore,
  checkpointEnabled: true,
  checkpointInterval: 1, // checkpoint after every task
  maxConcurrentWorkflows: 1,
  timeoutMs: 7200000, // 2 hours max
});

// Register the workflow
engine.registerWorkflow(abletonMixWorkflow);

// ── HTTP Agent Invoker ────────────────────────────────────────────────────────
function createPythonInvoker() {
  return async (task, context) => {
    const agentPort = AGENT_PORT;
    const baseUrl = `http://127.0.0.1:${agentPort}`;
    const taskUrl = `${baseUrl}/tasks`;

    try {
      const response = await fetch(taskUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          taskId: task.id,
          action: task.input?.action || task.name,
          context: context,
          resultsFrom: Object.fromEntries(taskResults),
        }),
        signal: AbortSignal.timeout(task.timeoutMs || 300000),
      });

      if (!response.ok) {
        throw new Error(`Agent error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      throw error;
    }
  };
}

// ── Start the workflow ────────────────────────────────────────────────────────
async function startWorkflow(config) {
  const execution = await engine.startWorkflow("ableton-mix", config);

  // Wire up event handlers for logging
  eventBus.subscribe("*", (event) => {
    console.log(`[event] ${event.type}: taskId=${event.taskId?.id || '?'} status=${event.taskId?.status}`);
  });

  return execution;
}

// ── Wait for completion ────────────────────────────────────────────────────────
function waitForCompletion(executionId, pollIntervalMs = 2000, maxWaitMs = 7200000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();

    const poll = () => {
      const exec = engine.getExecution(executionId);
      if (!exec) {
        reject(new Error(`Execution ${executionId} not found`));
        return;
      }

      if (exec.status === "completed" || exec.status === "failed" || exec.status === "cancelled") {
        resolve(exec);
        return;
      }

      if (Date.now() - start > maxWaitMs) {
        reject(new Error(`Timeout waiting for execution ${executionId}`));
        return;
      }

      setTimeout(poll, pollIntervalMs);
    };

    poll();
  });
}

// ── REST API ──────────────────────────────────────────────────────────────────
async function handleRequest(req, res) {
  const url = new URL(req.url, `http://localhost:${DEFAULT_PORT}`);

  // CORS + JSON headers
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  try {
    // ── POST /workflow/start ───────────────────────────────────────
    if (url.pathname === "/workflow/start" && req.method === "POST") {
      const config = await parseBody(req);
      console.log(`[bridge] Starting workflow with config:`, JSON.stringify(config).slice(0, 200));
      const execution = await startWorkflow(config);
      console.log(`[bridge] Execution started: ${execution.id}`);

      // Wait for completion in the background
      waitForCompletion(execution.id)
        .then((finalExec) => {
          console.log(`[bridge] Workflow ${finalExec.status} (id: ${finalExec.id})`);
        })
        .catch((err) => {
          console.error(`[bridge] Workflow error: ${err.message}`);
        });

      res.writeHead(200);
      res.end(JSON.stringify({
        executionId: execution.id,
        status: "running",
        message: "Workflow started",
      }));
      return;
    }

    // ── GET /workflow/:id/status ──────────────────────────────────────
    const statusMatch = url.pathname.match(/^\/workflow\/([^/]+)\/status$/);
    if (statusMatch && req.method === "GET") {
      const execId = statusMatch[1];
      const exec = engine.getExecution(execId);

      if (!exec) {
        res.writeHead(404);
        res.end(JSON.stringify({ error: "Execution not found" }));
        return;
      }

      res.writeHead(200);
      res.end(JSON.stringify({
        executionId: exec.id,
        status: exec.status,
        taskCount: exec.taskResults?.size || 0,
        context: exec.context,
      }));
      return;
    }

    // ── POST /workflow/:id/cancel ────────────────────────────────────
    const cancelMatch = url.pathname.match(/^\/workflow\/([^/]+)\/cancel$/);
    if (cancelMatch && req.method === "POST") {
      const execId = cancelMatch[1];
      const cancelled = await engine.cancelExecution(execId);

      res.writeHead(200);
      res.end(JSON.stringify({
        executionId: execId,
        cancelled,
      }));
      return;
    }

    // ── GET /health ────────────────────────────────────────────────
    if (url.pathname === "/health") {
      const activeExecs = Array.from(engine["activeExecutions"]?.keys?.() || []);
      res.writeHead(200);
      res.end(JSON.stringify({
        status: "ok",
        version: "1.0.0",
        bridge: "agentflow-ableton",
        workflow: "ableton-mix",
        activeExecutions: activeExecs.length,
        checkpointStore: checkpointStore ? "in-memory" : "none",
      }));
      return;
    }

    // ── 404 ────────────────────────────────────────────────────────
    res.writeHead(404);
    res.end(JSON.stringify({ error: "Not found" }));
  } catch (err) {
    console.error(`[bridge] Error: ${err.message}`);
    res.writeHead(500);
    res.end(JSON.stringify({ error: err.message }));
  }
}

async function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString()));
      } catch (err) {
        reject(err);
      }
    });
  });
}

// ── Start server ────────────────────────────────────────────────────────────────
const server = (await import("node:http")).default.createServer(handleRequest);
server.listen(DEFAULT_PORT, () => {
  console.log(`[agentflow-bridge] AgentFlow bridge running on port ${DEFAULT_PORT}`);
  console.log(`[agentflow-bridge] Expecting Python agents at http://127.0.0.1:${AGENT_PORT}/tasks`);
  console.log(`[agentflow-bridge] Endpoints: POST /workflow/start, GET /workflow/:id/status`);
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("[agentflow-bridge] Shutting down...");
  server.close(() => process.exit(0));
});
process.on("SIGINT", () => {
  console.log("[agentflow-bridge] Interrupted");
  server.close(() => process.exit(0));
});
