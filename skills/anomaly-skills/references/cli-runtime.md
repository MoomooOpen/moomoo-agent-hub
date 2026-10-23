# moomoo CLI runtime (anomaly skills)

Same probe and auth rules as `moomoo-quote`. Minimum CLI for `moomoo anomaly`: **TBD** — see `docs/migration-gaps-and-rest-api.md`.

macOS / Linux:

```bash
if command -v moomoo >/dev/null 2>&1; then moomoo auth status --format json; elif [ -x "$HOME/.moomoo/bin/moomoo" ]; then "$HOME/.moomoo/bin/moomoo" auth status --format json; else echo '__MOOMOO_CLI_MISSING__'; fi
```

Windows: use `%LOCALAPPDATA%\MoomooCLI\bin\moomoo.exe` per `moomoo-quote`.

- Missing CLI: offer [moomoo-cli install](https://github.com/MoomooOpen/moomoo-cli/blob/main/README.md) after consent.
- Not logged in: `moomoo auth login` before anomaly calls.
- Unknown `moomoo anomaly`: needs newer CLI; do not fall back to OpenD or Python SDK.

Append `--format json` and hidden `--source skill` on Bash invocations.
