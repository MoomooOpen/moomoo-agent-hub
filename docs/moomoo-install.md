# moomoo Skill Installation Guide

Install moomoo Skills into your AI client in three steps.

---

## Prerequisites

| Dependency | Purpose | Check |
|------------|---------|-------|
| `python3` | Runs anomaly-detection scripts and the `moomoo-skills` CLI | `python3 --version` |
| `curl` | Downloads the installer | `curl --version` |
| Node.js 18+ | Provides `npx` for `npx skills add` | `node -v` |

> macOS ships `python3` and `curl`. Linux: `apt install python3 curl` / `yum install python3 curl`. Windows: WSL or Git Bash + the official Node.js installer.

---

## Step 1 — Install the `moomoo-skills` CLI

`moomoo-skills` manages skill versions and self-upgrades.

```bash
curl -fsSL https://raw.githubusercontent.com/MoomooOpen/moomoo-agent-hub/feature/v20260512-add-skills/moomoo-install.sh | bash
```

Verify:

```bash
moomoo-skills --version
moomoo-skills check        # Check for skill updates
```

If `moomoo-skills` is not found, ensure `~/.local/bin` (or `/usr/local/bin`) is in your `PATH`, or open a new terminal.

---

## Step 2 — Install Skill Files

Install search and anomaly-detection skills into your AI client's skills directory:

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub#feature/v20260512-add-skills
```

> `-y` skips interactive selection; `-g` installs globally (all projects). Drop `-y` to pick skills interactively, or `-g` to install only into the current project.

Other useful invocations:

```bash
# Switch to another branch / tag / commit
npx skills add -y -g MoomooOpen/moomoo-agent-hub#<branch-or-tag>

# Upgrade installed skills
npx skills update moomoo-skill
```

### Per-Client Targets

`npx skills add` auto-detects Claude-family clients. For others, pass `--target` or paste manually.

| AI Client | Command / Setup | Scope |
|-----------|-----------------|-------|
| Claude Code / VS Code / Cursor / JetBrains (Claude plugin) | Default — writes to `~/.claude/skills/` | Global |
| OpenClaw | Send in chat: `Install moomoo Developers Skill from this Git repo: <git-url>` | Global |
| Cursor (built-in AI) | Add `--target cursor` -> `~/.cursor/rules/` | Global |
| JetBrains (built-in AI) | Add `--target junie` -> `~/.junie/guidelines/` | Global |
| VS Code (Cline / Roo Code) | Paste SKILL.md into `cline.customInstructions` / `roo-cline.customInstructions` | Global |
| Claude Desktop / Claude.ai | Paste SKILL.md into **Custom Instructions** | Global |

---

## Step 3 — Install OpenD (required for OpenAPI / Anomaly Skills)

OpenAPI Skills and Anomaly Detection Skills need the OpenD service running locally.

After Step 2 completes, invoke `/install-moomoo-opend` in your AI client. The skill directly downloads, installs, and starts OpenD (Windows / macOS / Linux supported) — no extra confirmation needed.

If `/install-moomoo-opend` is not registered, re-run Step 2 to make sure all skills from this repo are installed.

---

## Troubleshooting

<details>
<summary><b>Skill not found in chat</b></summary>

Some clients require a restart or a new chat session to pick up newly installed skills. Restart the client and retry in a fresh conversation.

</details>

<details>
<summary><b><code>npx skills add</code> fails</b></summary>

- Confirm Node.js 18+: `node -v`
- `command not found: skills` -> upgrade npm: `npm install -g npm@latest`
- Private-repo clone failure -> ensure an SSH key or HTTPS credential helper is configured for `github.com`; verify with a manual `git clone`
- Restricted network -> use HTTPS with a token: `npx skills add -y -g https://<token>@github.com/MoomooOpen/moomoo-agent-hub.git#feature/v20260512-add-skills`

</details>

<details>
<summary><b>OpenAPI connection fails</b></summary>

- OpenD must be running and logged in (status: connected)
- Default port `11111`
- If OpenD is not installed, run `/install-moomoo-opend` (see Step 3)

</details>
