#!/usr/bin/env node

/**
 * nowledge-mem-freebuff-sync
 *
 * Incremental sync for manicode/freebuff chat history into Nowledge Mem threads.
 * Uses .sync-state.json with SHA256 hashes to detect new/updated conversations.
 *
 * Usage:
 *   nowledge-mem-freebuff-sync --project <project_name>
 *   nowledge-mem-freebuff-sync --project <project_name> --apply
 *   nowledge-mem-freebuff-sync --dry-run --limit 5 --json
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SOURCE_APP = "freebuff";
const DEFAULT_API_URL = "<nmem_api_url>";
const CONFIG_PATH = join(homedir(), ".nowledge-mem", "config.json");
const STATE_FILE = ".sync-state.json";
const DEFAULT_MAX_MESSAGE_CHARS = 8000;
const DEFAULT_TIMEOUT_MS = 15_000;
const VERSION = readPackageVersion();

// ─── CLI parsing ────────────────────────────────────────────────────────────

function readPackageVersion() {
	try {
		const here = dirname(fileURLToPath(import.meta.url));
		const pkg = JSON.parse(readFileSync(resolve(here, "..", "package.json"), "utf8"));
		return typeof pkg.version === "string" ? pkg.version : "unknown";
	} catch {
		return "unknown";
	}
}

function usage() {
	return `Nowledge Mem freebuff (manicode/codebuff) historical chat sync

Preview sessions:
  knowledge-mem-freebuff-sync
  knowledge-mem-freebuff-sync --project <project_name> --dry-run --json

Import sessions:
  knowledge-mem-freebuff-sync --project <project_name> --apply
  knowledge-mem-freebuff-sync --project ~/.config/manicode/projects/myproject --apply --space work

Options:
  --project <name|path>    Project name or full path to ~/.config/manicode/projects/<name> or a custom path.
                           Without --project, scans all projects found in ~/.config/manicode/projects/.
  --apply                  Actually import sessions. Without this flag the command only previews.
  --dry-run                Same as --apply false; show what would be done without writing.
  --json                   Print machine-readable JSON report.
  --limit <n>              Limit imported/previewed sessions after filtering.
  --since <date>           Include sessions modified at or after this ISO date.
  --until <date>           Include sessions modified before this ISO date.
  --project-filter <text>  Include sessions whose project path contains this text.
  --space <id-or-name>     Route imported threads to a Mem space.
  --api-url <url>          Override NMEM_API_URL or ~/.nowledge-mem/config.json.
  --api-key <key>          Override NMEM_API_KEY or ~/.nowledge-mem/config.json.
  --agent-id <id>          Attribute messages to an AI Identity.
  --host-agent-id <id>     Attribute messages to a host-local agent identity.
  --max-message-chars <n>  Truncate individual messages after n characters (default ${DEFAULT_MAX_MESSAGE_CHARS}).
  --help                   Show this help.
`;
}

function parseArgs(argv) {
	const args = {
		apply: false,
		dryRun: false,
		json: false,
		project: undefined,
		limit: undefined,
		since: undefined,
		until: undefined,
		projectFilter: undefined,
		space: undefined,
		apiUrl: undefined,
		apiKey: undefined,
		agentId: undefined,
		hostAgentId: undefined,
		maxMessageChars: DEFAULT_MAX_MESSAGE_CHARS,
	};
	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		const value = () => {
			index += 1;
			if (index >= argv.length) throw new Error(`${arg} requires a value`);
			return argv[index];
		};
		if (arg === "--apply") args.apply = true;
		else if (arg === "--dry-run") args.dryRun = true;
		else if (arg === "--json") args.json = true;
		else if (arg === "--project") args.project = value();
		else if (arg === "--limit") args.limit = positiveInt(value(), "--limit");
		else if (arg === "--since") args.since = parseDate(value(), "--since");
		else if (arg === "--until") args.until = parseDate(value(), "--until");
		else if (arg === "--project-filter") args.projectFilter = value().toLowerCase();
		else if (arg === "--space") args.space = value().trim() || undefined;
		else if (arg === "--api-url") args.apiUrl = trimTrailingSlash(value());
		else if (arg === "--api-key") args.apiKey = value().trim() || undefined;
		else if (arg === "--agent-id") args.agentId = value().trim() || undefined;
		else if (arg === "--host-agent-id") args.hostAgentId = value().trim() || undefined;
		else if (arg === "--max-message-chars") args.maxMessageChars = positiveInt(value(), "--max-message-chars");
		else if (arg === "--help" || arg === "-h") {
			console.log(usage());
			process.exit(0);
		} else {
			throw new Error(`Unknown option: ${arg}`);
		}
	}
	args.apply = args.apply && !args.dryRun;
	return args;
}

function positiveInt(raw, name) {
	const parsed = Number.parseInt(raw, 10);
	if (!Number.isFinite(parsed) || parsed < 1) throw new Error(`${name} must be a positive integer`);
	return parsed;
}

function parseDate(raw, name) {
	const date = new Date(raw);
	if (Number.isNaN(date.getTime())) throw new Error(`${name} must be a valid ISO date`);
	return date;
}

function trimTrailingSlash(value) {
	return value.trim().replace(/\/+$/, "");
}

// ─── Config ──────────────────────────────────────────────────────────────────

function readSharedConfig() {
	try {
		if (!existsSync(CONFIG_PATH)) return {};
		const parsed = JSON.parse(readFileSync(CONFIG_PATH, "utf8"));
		return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
	} catch {
		return {};
	}
}

function resolveConfig(args) {
	const config = readSharedConfig();
	return {
		apiUrl: trimTrailingSlash(args.apiUrl || process.env.NMEM_API_URL?.trim() || config.apiUrl || config.api_url || DEFAULT_API_URL),
		apiKey: args.apiKey || process.env.NMEM_API_KEY?.trim() || config.apiKey || config.api_key,
		space: args.space || process.env.NMEM_SPACE?.trim() || process.env.NMEM_SPACE_ID?.trim() || config.space || config.spaceId || config.space_id,
		agentId: args.agentId || process.env.NMEM_AGENT_ID?.trim() || config.agentId || config.agent_id,
		hostAgentId: args.hostAgentId || process.env.NMEM_HOST_AGENT_ID?.trim() || config.hostAgentId || config.host_agent_id,
	};
}

// ─── Chat discovery ──────────────────────────────────────────────────────────

function discoverChats(baseDir, limit) {
	const entries = [];
	try {
		const names = readdirSync(baseDir);
		for (const name of names) {
			const chatDir = join(baseDir, name);
			let stats;
			try { stats = statSync(chatDir); } catch { continue; }
			if (!stats.isDirectory()) continue;
			const msgsFile = join(chatDir, "chat-messages.json");
			if (!existsSync(msgsFile)) continue;
			const size = stats.size;
			if (size < 400_000) continue; // skip stubs
			entries.push({ dir: chatDir, name, size });
		}
	} catch (e) {
		console.error(`Warning: cannot read ${baseDir}: ${e.message}`);
	}
	entries.sort((a, b) => b.name.localeCompare(a.name)); // newest first
	return limit ? entries.slice(0, limit) : entries;
}

// ─── Chat parsing ────────────────────────────────────────────────────────────

function extractTextFromBlocks(blocks) {
	const parts = [];
	for (const b of blocks || []) {
		if (b.type === "text") {
			const c = b.content;
			if (typeof c === "string") parts.push(c);
			else if (Array.isArray(c)) {
				for (const item of c) {
					if (item && typeof item === "object" && item.type === "text") {
						parts.push(item.text || "");
					}
				}
			}
		}
	}
	return parts.join("\n").trim();
}

function isDurableFact(text) {
	const processPats = /(?:让我先|接下来|我会|现在我需要|首先|然后|最后|好的，我来)/;
	if (processPats.test(text.slice(0, 100))) return false;
	const factPats = [
		/\d{6,}-signed\.bin/, /\bcommit\s+[a-f0-9]{7,}/, /\b0x[0-9a-fA-F]{4,}/,
		/\bBUGS?\.\w+/, /已修复|已确认|根因|解决方案|约束|规范/,
		/\bpartitions\.csv\b|\bslot.*size|\bnvs.*offset/,
		/\bmeta-pass\b|\bpass-radar\b|\bfreebuff\b|\bmanicode\b/,
	];
	return factPats.some(p => p.test(text));
}

function loadState(projectPath) {
	const stateFile = join(projectPath, STATE_FILE);
	if (!existsSync(stateFile)) return { chats: {}, lastSync: null };
	try { return JSON.parse(readFileSync(stateFile, "utf8")); } catch { return { chats: {}, lastSync: null }; }
}

function saveState(projectPath, state) {
	state.lastSync = new Date().toISOString();
	writeFileSync(join(projectPath, STATE_FILE), JSON.stringify(state, null, 2) + "\n");
}

function chatHash(chatDir) {
	const f = join(chatDir, "chat-messages.json");
	if (!existsSync(f)) return null;
	return createHash("sha256").update(readFileSync(f)).digest("hex").slice(0, 16);
}

// ─── Session → thread body ───────────────────────────────────────────────────

function buildThreadBody(chatDir, ts, facts, runstate) {
	const title = facts.length > 0
		? facts[0].title.slice(0, 120)
		: `freebuff session ${ts}`;
	const messages = [];
	for (const f of facts) {
		messages.push({
			role: "user",
			content: f.content,
			timestamp: ts,
			metadata: { external_id: `${f.type}-fact-${createHash("sha256").update(f.content).digest("hex").slice(0, 10)}`, source_app: SOURCE_APP },
		});
	}
	if (runstate) {
		messages.push({
			role: "assistant",
			content: runstate.content,
			timestamp: ts + "_runstate",
			metadata: { external_id: "runstate", source_app: SOURCE_APP },
		});
	}
	return {
		thread_id: `freebuff-${ts}`,
		title,
		messages,
		source: SOURCE_APP,
		project: chatDir.replace(/.*\/projects\//, ""),
		metadata: {
			freebuff_session_id: ts,
			freebuff_chat_dir: chatDir,
			fact_count: facts.length,
			historical_import: true,
			import_tool_version: VERSION,
		},
	};
}

// ─── API POST ────────────────────────────────────────────────────────────────

async function postJson(config, path, body) {
	const headers = { "Content-Type": "application/json" };
	if (config.apiKey) {
		headers["Authorization"] = `Bearer ${config.apiKey}`;
		headers["X-NMEM-API-Key"] = config.apiKey;
	}
	let url;
	try { url = new URL(path, config.apiUrl).href; } catch { return { ok: false, status: 0, error: "bad url" }; }
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
	try {
		const resp = await fetch(url, { method: "POST", headers, body: JSON.stringify(body), signal: controller.signal });
		const data = await resp.json().catch(() => ({}));
		return { ok: resp.ok, status: resp.status, data };
	} catch (e) {
		return { ok: false, status: 0, error: e.message };
	} finally { clearTimeout(timer); }
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
	const args = parseArgs(process.argv.slice(2));
	const config = resolveConfig(args);

	// Determine base dir
	let baseDir;
	if (args.project) {
		const p = resolve(args.project);
		baseDir = existsSync(join(p, "chats")) ? join(p, "chats") : join(p);
	} else {
		baseDir = join(homedir(), ".config", "manicode", "projects");
	}
	if (!existsSync(baseDir)) {
		console.error(`Error: base dir not found: ${baseDir}`);
		process.exit(1);
	}

	// Discover sub-projects
	const projectNames = readdirSync(baseDir).filter(n => {
		const d = join(baseDir, n);
		return statSync(d).isDirectory() && existsSync(join(d, "chats"));
	}).map(n => ({ name: n, dir: join(baseDir, n) }));

	if (!args.project && projectNames.length === 0) {
		console.log("No manicode projects found.");
		return;
	}

	const results = [];
	for (const proj of projectNames) {
		const projectChatsDir = join(proj.dir, "chats");
		const chats = discoverChats(projectChatsDir, args.limit || 9999);
		const state = loadState(proj.dir);
		const newChats = chats.filter(c => state.chats[c.name]?.hash !== chatHash(c.dir));

		for (const chat of newChats) {
			const ts = chat.name;
			const msgsFile = join(chat.dir, "chat-messages.json");
			let data;
			try { data = JSON.parse(readFileSync(msgsFile, "utf8")); } catch { continue; }

			const aiMessages = (data || []).filter(m => m.variant === "ai" && m.blocks);
			const facts = [];
			for (const m of aiMessages) {
				const txt = extractTextFromBlocks(m.blocks);
				if (!txt || txt.length < 150 || !isDurableFact(txt)) continue;
				const lines = txt.split("\n").map(l => l.trim()).filter(l => l.length > 10);
				facts.push({ type: "fact", title: (lines[0] || "Fact").slice(0, 80), content: txt.slice(0, args.maxMessageChars) });
				if (facts.length >= 5) break;
			}

			// Run-state
			let runstate = null;
			const rsFile = join(chat.dir, "run-state.json");
			if (existsSync(rsFile)) {
				try {
					const rs = JSON.parse(readFileSync(rsFile, "utf8"));
					const out = rs.output || {};
					if (out.type === "lastMessage") {
						for (const m of out.value || []) {
							if (!m || !Array.isArray(m.content)) continue;
							for (const c of m.content) {
								if (c?.type === "text" && c.text?.length > 100) {
									runstate = { type: "runstate", title: `[交付物] ${c.text.slice(0, 50)}`, content: c.text.slice(0, 800) };
								}
							}
						}
					} else if (out.type === "error") {
						runstate = { type: "interrupted", title: "[中断标记] 会话以错误结束，有未完成进度", content: `trace=${rs.traceSessionId || "unknown"}` };
					}
				} catch {}
			}

			if (facts.length === 0 && !runstate) continue;

			const body = buildThreadBody(chat.dir, ts, facts, runstate);
			const threadId = `freebuff-${ts}`;

			if (!args.apply) {
				results.push({ threadId, project: proj.name, chatDir: chat.dir, title: body.title, messageCount: body.messages.length, action: "ready" });
				continue;
			}

			// Post to nmem threads API
			const createResult = await postJson(config, "/threads", body);
			if (!createResult.ok) {
				results.push({ threadId, project: proj.name, chatDir: chat.dir, action: "failed", error: createResult.error || JSON.stringify(createResult.data)?.slice(0, 200) });
				continue;
			}
			results.push({ threadId, project: proj.name, chatDir: chat.dir, title: body.title, messageCount: body.messages.length, action: "created", thread: createResult.data?.thread?.id });

			// Update state
			state.chats[ts] = { hash: chatHash(chat.dir), timestamp: new Date().toISOString() };
			saveState(proj.dir, state);
		}
	}

	// Report
	const report = {
		apply: args.apply,
		found: results.length,
		created: results.filter(r => r.action === "created").length,
		failed: results.filter(r => r.action === "failed").length,
		sessions: results,
	};

	if (args.json) {
		console.log(JSON.stringify(report, null, 2));
	} else {
		console.log(`Scanned ${results.length} new session(s)`);
		if (args.apply) console.log(`Created: ${report.created}  Failed: ${report.failed}`);
		else console.log("No changes made. Re-run with --apply to import.");
		for (const s of results.slice(0, 10)) {
			console.log(`  ${s.action.toUpperCase()}: ${s.threadId}  messages=${s.messageCount || 0}  ${s.title?.slice(0, 80) || ""}`);
		}
		if (results.length > 10) console.log(`... ${results.length - 10} more; use --json for full output.`);
	}
	if (report.failed > 0) process.exitCode = 1;
}

main().catch(err => { console.error(err instanceof Error ? err.message : String(err)); process.exit(1); });
