# moomoo Skill Installation Guide

Install moomoo Skills into your AI client in two steps.

---

## Prerequisites

| Dependency | Purpose | Check |
|------------|---------|-------|
| `curl` | Content skills and CLI installer download | `curl --version` |
| Node.js 18+ | Provides `npx` for `npx skills add` | `node -v` |
| `moomoo` CLI | Quote, trading, and anomaly skills | `moomoo version` |

> Upgrading from OpenD: [upgrade-from-opend.md](./upgrade-from-opend.md). Gaps and REST backlog: [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md).

---

## Step 1 — Install Skill Files

Install search and anomaly-detection skills into your AI client's skills directory:

```bash
npx skills add -y -g MoomooOpen/moomoo-agent-hub#main
```

> `-y` skips interactive selection; `-g` installs globally (all projects). Drop `-y` to pick skills interactively, or `-g` to install only into the current project.

Other useful invocations:

```bash
# Switch to another branch / tag / commit
npx skills add -y -g MoomooOpen/moomoo-agent-hub#<branch-or-tag>

# Upgrade one installed skill
npx skills update <slug> -g -y
```

`npx skills update` refreshes the current slug and leaves a renamed directory in place. If an older short name is still installed (`news-search`, `stock-digest`, `comment-sentiment`, `install-opend`, `capital-anomaly`, `derivatives-anomaly`, `technical-anomaly`), remove it once, then install again:

```bash
bash scripts/migrate-renamed-skills.sh
npx skills add -y -g MoomooOpen/moomoo-agent-hub
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

## Step 2 — Install and authorize moomoo CLI

Quote, trading, and anomaly skills use the **`moomoo` CLI** (OAuth). OpenD is **not** required.

```bash
moomoo version
moomoo auth login
moomoo auth status --format json
moomoo check
```

Anomaly skills use `moomoo anomaly ...` when available — see [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md).

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
- Restricted network -> use HTTPS with a token: `npx skills add -y -g https://<token>@github.com/MoomooOpen/moomoo-agent-hub.git#main`

</details>

<details>
<summary><b><code>moomoo</code> CLI fails</b></summary>

- Run `moomoo auth status` — if not logged in, run `moomoo auth login`
- Run `moomoo check`
- Unknown `moomoo anomaly`: see [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md)

</details>
