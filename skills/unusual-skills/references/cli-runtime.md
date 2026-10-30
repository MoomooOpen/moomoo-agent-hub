# moomoo CLI runtime (Unusual skills)

Unusual skills (`moomoo-unusual-*`) use the same probe and auth as `moomoo-quote`. Top-level command: **`moomoo unusual`** (`anomaly` is a compatibility alias). Minimum CLI version: see `docs/migration-gaps-and-rest-api.md`.

| Skill | Command |
|-------|---------|
| Unusual Capital Flows | `moomoo unusual capital-flows <symbol>` |
| Unusual Derivatives Activity | `moomoo unusual derivatives-activity <symbol>` |
| Technical Signal Alerts | `moomoo unusual technical-signals <symbol>` |

macOS / Linux:

```bash
if command -v moomoo >/dev/null 2>&1; then moomoo auth status --format json; elif [ -x "$HOME/.moomoo/bin/moomoo" ]; then "$HOME/.moomoo/bin/moomoo" auth status --format json; else echo '__MOOMOO_CLI_MISSING__'; fi
```

Windows: `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe` per `moomoo-quote`.

- Missing CLI: offer [moomoo-cli install](https://github.com/MoomooOpen/moomoo-cli/blob/main/README.md) after consent.
- Not logged in: `moomoo auth login` before unusual commands.
- Unknown `moomoo unusual`: needs newer CLI; do not fall back to OpenD or Python SDK.

Append `--format json` and hidden `--source skill` on Bash invocations.
