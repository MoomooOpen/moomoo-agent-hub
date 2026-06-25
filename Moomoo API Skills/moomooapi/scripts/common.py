#!/usr/bin/env python3
"""
Common utility module - Provides shared functionality for Futu OpenAPI scripts

Includes:
- Environment variable configuration
- Dependency checking and auto-installation
- OpenD connection configuration
- Trading environment/market enum conversion
- Context management helpers
"""
import os
import subprocess
import sys
import json
import tempfile
import time
from dataclasses import dataclass
from typing import Optional


# ============================================================
# Environment Variable Configuration
# ============================================================

@dataclass
class FutuConfig:
    """Futu OpenAPI configuration class"""
    # Login credentials
    login_account: Optional[str] = None
    login_pwd: Optional[str] = None

    # OpenD connection configuration
    opend_host: str = "127.0.0.1"
    opend_port: int = 11111

    # Trading configuration
    trd_env: str = "SIMULATE"
    default_market: str = "NONE"
    security_firm: Optional[str] = None


def get_config() -> FutuConfig:
    """
    Get Futu OpenAPI configuration

    Reads configuration from environment variables, using defaults for unset values.

    Environment variables:
        - FUTU_LOGIN_ACCOUNT: Futu login account
        - FUTU_LOGIN_PWD: Futu login password
        - FUTU_OPEND_HOST: OpenD host address (default: 127.0.0.1)
        - FUTU_OPEND_PORT: OpenD port (default: 11111)
        - FUTU_TRD_ENV: Trading environment (default: SIMULATE)
        - FUTU_DEFAULT_MARKET: Default market (default: US)

    Returns:
        FutuConfig: Configuration object
    """
    return FutuConfig(
        login_account=os.getenv("FUTU_LOGIN_ACCOUNT", ""),
        login_pwd=os.getenv("FUTU_LOGIN_PWD", ""),
        opend_host=os.getenv("FUTU_OPEND_HOST", "127.0.0.1"),
        opend_port=int(os.getenv("FUTU_OPEND_PORT", "11111")),
        trd_env=os.getenv("FUTU_TRD_ENV", "SIMULATE"),
        default_market=os.getenv("FUTU_DEFAULT_MARKET", "NONE"),
        security_firm=os.getenv("FUTU_SECURITY_FIRM", "") or None,
    )


def _ensure_utf8_io():
    """Switch stdout/stderr to UTF-8 on Windows to avoid GBK encoding errors"""
    if sys.platform != "win32":
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


_ensure_utf8_io()


# ============================================================
# Dependency Checking
# ============================================================

SDK_MODULE_NAME = "moomoo"  # Fixed brand module name

# Must match install-moomoo-opend SKILL.md metadata.version
# Version stamp file is auto-generated after running /install-moomoo-opend skill to install OpenD
SKILL_VERSION = "0.1.1"
STAMP_FILE = os.path.join(os.path.expanduser("~"), ".moomoo_skill_version")

MIN_SDK_VERSION = "10.4.6408"
# OpenCryptoTradeContext was introduced in 10.5.6508; crypto scripts require this version
MIN_CRYPTO_SDK_VERSION = "10.5.6508"

# ai_type parameter requires SDK >= MIN_SDK_VERSION; skip for older versions
_sdk_supports_ai_type = True

# Environment check cache: write temp file after first full check, skip within TTL
_ENV_CHECK_CACHE_FILE = os.path.join(tempfile.gettempdir(), ".moomoo_env_ok")
_ENV_CHECK_TTL = 3600  # 1 hour


def _parse_version(ver_str):
    """Parse version string into comparable tuple, e.g. '10.4.6408' -> (10, 4, 6408)"""
    try:
        return tuple(int(x) for x in ver_str.strip().split("."))
    except (ValueError, AttributeError):
        return (0,)


def _env_check_is_cached():
    """Check if a recent successful environment check exists"""
    try:
        mtime = os.path.getmtime(_ENV_CHECK_CACHE_FILE)
        return (time.time() - mtime) < _ENV_CHECK_TTL
    except OSError:
        return False


def _env_check_mark_ok():
    """Mark environment check as passed"""
    try:
        with open(_ENV_CHECK_CACHE_FILE, "w") as f:
            f.write(str(time.time()))
    except OSError:
        pass


def _check_version_stamp():
    """Check version stamp file to ensure OpenD and SDK were properly installed (warn only, non-blocking)"""
    try:
        with open(STAMP_FILE, "r", encoding="utf-8") as f:
            installed = f.read().strip()
    except FileNotFoundError:
        print(f"[WARN] Version stamp file not found: {STAMP_FILE}. Consider running /install-moomoo-opend to install", file=sys.stderr)
        return
    if installed != SKILL_VERSION:
        print(f"[WARN] Version mismatch: installed {installed}, required {SKILL_VERSION}. Consider running /install-moomoo-opend to update", file=sys.stderr)


def _check_opend_reachable():
    """Check if OpenD is reachable"""
    import socket
    config = get_config()
    host, port = config.opend_host, config.opend_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
    except (ConnectionRefusedError, OSError) as e:
        print(f"[ERROR] Cannot connect to OpenD ({host}:{port}): {e}")
        print("Please start the OpenD client first")
        sys.exit(1)
    finally:
        sock.close()


def _detect_ai_type_support():
    """Detect whether current SDK supports ai_type parameter (version check only, no warning)"""
    global _sdk_supports_ai_type
    try:
        import moomoo
        current = getattr(moomoo, "__version__", "0")
        if _parse_version(current) < _parse_version(MIN_SDK_VERSION):
            _sdk_supports_ai_type = False
    except ImportError:
        pass


def ensure_futu_api():
    """Environment check with cache: SDK version + stamp + OpenD connectivity. Full check on first run, skip within TTL."""
    # 1. Cache hit — only do lightweight ai_type support detection
    if _env_check_is_cached():
        _detect_ai_type_support()
        return True

    # 2. Version stamp check
    _check_version_stamp()

    # 3. SDK import + version check
    global _sdk_supports_ai_type
    try:
        import moomoo
        current = getattr(moomoo, "__version__", "0")
        if _parse_version(current) < _parse_version(MIN_SDK_VERSION):
            _sdk_supports_ai_type = False
            print(f"[WARN] moomoo-api version too low: {current} < {MIN_SDK_VERSION}. ai_type parameter will be skipped. Consider running /install-moomoo-opend to upgrade SDK", file=sys.stderr)
    except ImportError:
        print("[ERROR] moomoo-api not installed. Please run /install-moomoo-opend")
        sys.exit(1)

    # 4. OpenD connectivity check
    _check_opend_reachable()

    # 5. Mark check passed
    _env_check_mark_ok()
    return True

ensure_futu_api()

from moomoo import (
        OpenQuoteContext,
        OpenSecTradeContext,
        RET_OK,
        TrdEnv,
        TrdMarket,
        TrdSide,
        OrderType,
        ModifyOrderOp,
        SubType,
        Session,
        KLType,
        AuType,
        Market,
        SecurityType,
        SecurityReferenceType,
        SimpleFilter,
        AccumulateFilter,
        FinancialFilter,
        FinancialQuarter,
        StockField,
        SortDir,
        Plate,
        OrderBookType,
)

try:
    from moomoo import TradeDateMarket
except ImportError:
    TradeDateMarket = None

from moomoo import SecurityFirm

try:
    from moomoo import OpenCryptoTradeContext
except ImportError:
    OpenCryptoTradeContext = None

try:
    from moomoo import TimeInForce
except ImportError:
    TimeInForce = None


# ============================================================
# Connection Configuration
# ============================================================

def get_opend_config():
    """Get OpenD connection configuration -> (host, port)"""
    config = get_config()
    return config.opend_host, config.opend_port


def _check_opend_alive(host, port):
    """Quick check if OpenD port is reachable, exit with error if not"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Error: Cannot connect to OpenD ({host}:{port}), connection refused. Please start the OpenD client first.")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Cannot connect to OpenD ({host}:{port}): {e}. Please check if OpenD is running.")
        sys.exit(1)
    finally:
        sock.close()


def create_quote_context():
    """Create a quote context"""
    host, port = get_opend_config()
    _check_opend_alive(host, port)
    kwargs = dict(host=host, port=port)
    if _sdk_supports_ai_type:
        kwargs["ai_type"] = 1
    return OpenQuoteContext(**kwargs)


def parse_security_firm(firm_str):
    """Parse security firm string -> SecurityFirm enum, returns None if invalid"""
    if not firm_str:
        return None
    key = str(firm_str).strip().upper()
    if hasattr(SecurityFirm, key):
        return getattr(SecurityFirm, key)
    return None


def get_default_security_firm():
    """Get default security firm (from environment variable)"""
    config = get_config()
    return parse_security_firm(config.security_firm)


def create_trade_context(market=None, security_firm=None):
    """Create a trade context"""
    host, port = get_opend_config()
    _check_opend_alive(host, port)
    trd_market = parse_market(market) if market else get_default_market()
    kwargs = dict(host=host, port=port, filter_trdmarket=trd_market)
    if _sdk_supports_ai_type:
        kwargs["ai_type"] = 1
    if security_firm is not None:
        kwargs["security_firm"] = security_firm
    else:
        default_firm = get_default_security_firm()
        kwargs["security_firm"] = default_firm if default_firm is not None else SecurityFirm.NONE
    return OpenSecTradeContext(**kwargs)


# Crypto trading context supports only FUTUSECURITIES (HK), FUTUINC (US), FUTUSG (SG)
CRYPTO_SUPPORTED_FIRMS = ("FUTUSECURITIES", "FUTUINC", "FUTUSG")

# Crypto firm auto-detect cache to avoid probing all firms on every call
_CRYPTO_FIRM_CACHE_FILE = os.path.join(tempfile.gettempdir(), ".moomoo_crypto_firm")
_CRYPTO_FIRM_CACHE_TTL = 3600


def _crypto_firm_cache_read():
    try:
        if (time.time() - os.path.getmtime(_CRYPTO_FIRM_CACHE_FILE)) >= _CRYPTO_FIRM_CACHE_TTL:
            return None
        with open(_CRYPTO_FIRM_CACHE_FILE, "r", encoding="utf-8") as f:
            name = f.read().strip()
        return name if name in CRYPTO_SUPPORTED_FIRMS else None
    except OSError:
        return None


def _crypto_firm_cache_write(firm_name):
    try:
        with open(_CRYPTO_FIRM_CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(firm_name)
    except OSError:
        pass


def _crypto_firm_cache_clear():
    try:
        os.remove(_CRYPTO_FIRM_CACHE_FILE)
    except OSError:
        pass


def _build_crypto_ctx(firm_enum, host, port):
    kwargs = dict(host=host, port=port, security_firm=firm_enum)
    if _sdk_supports_ai_type:
        import inspect as _inspect
        try:
            if "ai_type" in _inspect.signature(OpenCryptoTradeContext).parameters:
                kwargs["ai_type"] = 1
        except (TypeError, ValueError):
            pass
    return OpenCryptoTradeContext(**kwargs)


def _probe_crypto_firm(firm, host, port):
    """Probe whether the given firm has an available CRYPTO account."""
    ctx = None
    try:
        ctx = _build_crypto_ctx(firm, host, port)
        ret, data = ctx.get_acc_list()
        return ret == RET_OK and not is_empty(data)
    except Exception:
        return False
    finally:
        safe_close(ctx)


def _detect_crypto_firm(host, port):
    """Probe CRYPTO_SUPPORTED_FIRMS to find one with a real crypto account.

    Cached entries are still probed once, so a stale cache (e.g. after the user
    switched OpenD accounts) is automatically invalidated.
    """
    cached = _crypto_firm_cache_read()
    if cached is not None:
        firm = getattr(SecurityFirm, cached, None)
        if firm is not None and _probe_crypto_firm(firm, host, port):
            return firm
        _crypto_firm_cache_clear()

    for name in CRYPTO_SUPPORTED_FIRMS:
        firm = getattr(SecurityFirm, name, None)
        if firm is None:
            continue
        if _probe_crypto_firm(firm, host, port):
            _crypto_firm_cache_write(name)
            return firm
    return None


def create_crypto_trade_context(security_firm=None):
    """Create a crypto trade context (OpenCryptoTradeContext).

    security_firm precedence: argument > MOOMOO_SECURITY_FIRM env > auto-detect.
    Only FUTUSECURITIES, FUTUINC, FUTUSG are supported.
    """
    if OpenCryptoTradeContext is None:
        try:
            import moomoo as _mm
            cur = getattr(_mm, "__version__", "unknown")
        except ImportError:
            cur = "unknown"
        print(f"Error: Current moomoo-api {cur} does not provide OpenCryptoTradeContext. Crypto requires >= {MIN_CRYPTO_SDK_VERSION}. "
              f"Run: pip install --upgrade \"moomoo-api>={MIN_CRYPTO_SDK_VERSION}\"")
        sys.exit(1)
    host, port = get_opend_config()
    _check_opend_alive(host, port)

    use_json = "--json" in sys.argv

    firm_enum = security_firm
    if firm_enum is None:
        firm_enum = get_default_security_firm()
    if firm_enum is None:
        firm_enum = _detect_crypto_firm(host, port)
    if firm_enum is None:
        msg = (f"No crypto account found in {', '.join(CRYPTO_SUPPORTED_FIRMS)}. "
               f"Confirm crypto trading is enabled or pass --security-firm explicitly.")
        if use_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    firm_name = format_enum(firm_enum)
    if firm_name not in CRYPTO_SUPPORTED_FIRMS:
        msg = f"Crypto trading only supports {', '.join(CRYPTO_SUPPORTED_FIRMS)}. Got security_firm={firm_name}"
        if use_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    return _build_crypto_ctx(firm_enum, host, port)


# ============================================================
# Enum Conversion
# ============================================================

def parse_trd_env(env_str):
    """Parse trading environment string -> TrdEnv"""
    if env_str and str(env_str).upper() == "REAL":
        return TrdEnv.REAL
    return TrdEnv.SIMULATE


def parse_market(market_str):
    """Parse trading market string -> TrdMarket"""
    if not market_str:
        return TrdMarket.US
    mapping = {
        "NONE": TrdMarket.NONE,
        "US": TrdMarket.US,
        "HK": TrdMarket.HK,
        "CN": TrdMarket.CN,
        "HKCC": TrdMarket.HKCC,
        "SG": TrdMarket.SG,
    }
    if hasattr(TrdMarket, "MY"):
        mapping["MY"] = TrdMarket.MY
    if hasattr(TrdMarket, "JP"):
        mapping["JP"] = TrdMarket.JP
    if hasattr(TrdMarket, "CRYPTO"):
        mapping["CRYPTO"] = TrdMarket.CRYPTO
        mapping["CC"] = TrdMarket.CRYPTO
    return mapping.get(str(market_str).upper(), TrdMarket.US)


# CLI --market choices for trade scripts (SG/MY/JP require matching TrdMarket enum in SDK)
TRD_MARKET_CLI_CHOICES = ["US", "HK", "HKCC", "CN", "SG", "MY", "JP"]


# Stock code prefix -> Trading market mapping
_CODE_PREFIX_TO_MARKET = {
    "US": "US",
    "HK": "HK",
    "SH": "CN",
    "SZ": "CN",
    "SG": "SG",
    "MY": "MY",
    "JP": "JP",
    "CC": "CRYPTO",
}


def is_crypto_code(code):
    """Check if the code is a crypto code (CC. prefix)."""
    if not code or "." not in code:
        return False
    return code.split(".")[0].upper() == "CC"


def parse_qty(qty_str, code=None):
    """Parse order quantity: crypto allows float, others must be positive integer.

    - Crypto (CC. prefix): float allowed
    - Others: must be positive integer, else raises ValueError
    """
    if qty_str is None:
        raise ValueError("Quantity cannot be empty")
    try:
        val = float(qty_str)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity: {qty_str}")
    if val <= 0:
        raise ValueError("Quantity must be positive")
    if is_crypto_code(code):
        return val
    if float(val).is_integer():
        return int(val)
    raise ValueError(f"Non-crypto quantity must be integer, got: {qty_str}")


def infer_market_from_code(code):
    """Infer trading market string from stock code prefix, e.g. US.AAPL -> 'US', HK.00700 -> 'HK'.
    Returns None if unrecognizable."""
    if not code or "." not in code:
        return None
    prefix = code.split(".")[0].upper()
    return _CODE_PREFIX_TO_MARKET.get(prefix)


def parse_trd_side(side_str):
    """Parse trading side string -> TrdSide"""
    if not side_str or str(side_str).strip().upper() not in ("BUY", "SELL"):
        raise ValueError(f"Invalid trading side: {side_str}, must be BUY or SELL")
    if str(side_str).strip().upper() == "BUY":
        return TrdSide.BUY
    return TrdSide.SELL


def parse_subtypes(subtype_names):
    """Convert a list of strings to SubType enum list"""
    subtypes = []
    for name in subtype_names:
        key = str(name).strip().upper()
        if key == "BASIC":
            key = "QUOTE"
        if not hasattr(SubType, key):
            raise ValueError(f"Unsupported subscription type: {name}")
        subtypes.append(getattr(SubType, key))
    return subtypes


# ============================================================
# Configuration Retrieval
# ============================================================

def get_default_acc_id():
    """Get default account ID"""
    return int(os.getenv("FUTU_ACC_ID", "0"))


def get_default_trd_env():
    """Get default trading environment"""
    config = get_config()
    return parse_trd_env(config.trd_env)


def get_default_market():
    """Get default trading market"""
    config = get_config()
    return parse_market(config.default_market)



# ============================================================
# Data Processing Helpers
# ============================================================

def safe_get(row, *keys, default=""):
    """Safely get a value from a DataFrame row or dict, supports multiple fallback keys"""
    for key in keys:
        val = row.get(key) if hasattr(row, 'get') else getattr(row, key, None)
        if val is not None:
            return val
    return default


def safe_float(val, default=0.0):
    """Safely convert to float, returns default for N/A, empty string, None, etc."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=0):
    """Safely convert to int, returns default for N/A, empty string, None, etc.
    Handles numpy scalar types to avoid precision loss for large integers (e.g. 18-digit acc_id) via float64."""
    if val is None:
        return default
    # numpy scalar: extract native Python type to avoid float64 precision loss
    if hasattr(val, 'item'):
        val = val.item()
    try:
        return int(val)
    except (ValueError, TypeError):
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default


def format_enum(val):
    """Format enum value as string"""
    if hasattr(val, "name"):
        return val.name
    return str(val)


# ============================================================
# Context Management Helpers
# ============================================================

def safe_close(ctx):
    """Safely close a context"""
    try:
        if ctx:
            ctx.close()
    except Exception:
        pass


def _is_no_account_error(error_msg):
    """Check if the error indicates no available trading account (distinct from quote permission)."""
    msg = str(error_msg).lower()
    keywords = [
        "no available real accounts",
        "no available accounts",
        "no available simulate accounts",
        "无可用账户", "无可用交易账户", "没有可用账户",
    ]
    return any(kw in msg for kw in keywords)


def _is_unlock_needed_error(error_msg):
    """Check if the error indicates trade is not unlocked."""
    msg = str(error_msg).lower()
    keywords = [
        "没有解锁交易", "请先解锁交易", "未解锁交易", "交易未解锁",
        "unlock needed", "trade not unlocked", "trade unlock",
        "please unlock", "need unlock",
    ]
    return any(kw in msg for kw in keywords)


def _is_permission_error(error_msg):
    """Check if the error message indicates insufficient quote permissions. Account errors take precedence."""
    if _is_no_account_error(error_msg) or _is_unlock_needed_error(error_msg):
        return False
    keywords = [
        "权限", "没有权限", "权限不足", "无权限",
        "no permission", "permission denied", "not permission",
        "authority", "no authority",
        "quota", "no quota",
        "bmp", "lv1", "lv2",
        "未开通", "未购买", "need subscribe",
        "not subscribed", "unsubscribed",
    ]
    msg = str(error_msg).lower()
    return any(kw in msg for kw in keywords)


_MARKET_NAMES = {
    "HK": "HK stocks", "US": "US stocks",
    "SH": "A-shares", "SZ": "A-shares",
    "SG": "Singapore",
    "MY": "Malaysia stocks",
    "JP": "Japan stocks",
}

_AUTHORITY_URLS = {"moomoo": "https://openapi.moomoo.com/moomoo-api-doc/en/intro/authority.html"}


def _detect_market_from_argv():
    """Detect market from stock code in command-line arguments (e.g. HK.00700 -> HK stocks)"""
    import re
    for arg in sys.argv[1:]:
        m = re.match(r'^(HK|US|SH|SZ|SG|MY|JP)\.', arg, re.IGNORECASE)
        if m:
            return _MARKET_NAMES.get(m.group(1).upper(), "")
    return ""


def _get_authority_url():
    """Return the quote permission page URL"""
    return _AUTHORITY_URLS["moomoo"]



def _build_permission_hint():
    """Build a hint message for insufficient quote permissions"""
    market = _detect_market_from_argv()
    market_prefix = f"{market} " if market else ""
    url = _get_authority_url()
    return (
        f"\n\n{market_prefix}quote permissions insufficient. Please purchase the corresponding quote package to access data. "
        f"Details: {url}"
    )



def _build_permission_hint_json():
    """Build JSON-format quote permission hint fields"""
    market = _detect_market_from_argv()
    market_prefix = f"{market} " if market else ""
    hint = f"{market_prefix}quote permissions insufficient. Please purchase the corresponding quote package to access data"
    url = _get_authority_url()
    return {"hint": hint, "authority_url": url}



_NO_ACCOUNT_HINT = (
    "No available trading account found. Common causes: 1) The selected security_firm has no "
    "trading account for the target market; 2) the account logged into OpenD does not match the "
    "target account; 3) crypto accounts must first be opened in the Futu/Moomoo app. "
    "Adjust --security-firm / MOOMOO_SECURITY_FIRM or MOOMOO_TRD_ENV and retry."
)

_UNLOCK_NEEDED_HINT = (
    "Real trading is not unlocked. Please click 'Unlock Trade' in the OpenD GUI and enter your "
    "trade password to unlock, then retry placing/cancelling the order. For safety, this skill "
    "does not call unlock_trade through the SDK."
)


def check_ret(ret, data, ctx=None, action="operation", output_json=None):
    """Check API return value, print error and exit on failure"""
    if ret != RET_OK:
        if output_json is None:
            try:
                output_json = "--json" in sys.argv
            except Exception:
                output_json = False

        no_acc_error = _is_no_account_error(data)
        unlock_error = (not no_acc_error) and _is_unlock_needed_error(data)
        perm_error = (not no_acc_error) and (not unlock_error) and _is_permission_error(data)

        if output_json:
            err_obj = {"ret": ret, "action": action, "error": str(data)}
            if no_acc_error:
                err_obj["hint"] = _NO_ACCOUNT_HINT
            elif unlock_error:
                err_obj["hint"] = _UNLOCK_NEEDED_HINT
            elif perm_error:
                err_obj.update(_build_permission_hint_json())
            print(json.dumps(err_obj, ensure_ascii=False))
        else:
            print(f"{action} failed: {data}")
            if no_acc_error:
                print(f"\n{_NO_ACCOUNT_HINT}")
            elif unlock_error:
                print(f"\n{_UNLOCK_NEEDED_HINT}")
            elif perm_error:
                print(_build_permission_hint())
        safe_close(ctx)
        sys.exit(1)


def is_empty(data):
    """Check if data is empty"""
    if data is None:
        return True
    if hasattr(data, "shape"):
        return data.shape[0] == 0
    if hasattr(data, "__len__"):
        return len(data) == 0
    return False


def to_jsonable(val, default=None):
    """Convert a value to a JSON-serializable type"""
    import math
    if val is None:
        return default
    if hasattr(val, "item"):
        val = val.item()
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return default
    if hasattr(val, "name"):
        return val.name
    if isinstance(val, (str, int, float, bool, list, dict)):
        return val
    return str(val)


def df_to_records(df, limit=None):
    """Convert a DataFrame to a JSON-serializable list of records"""
    if is_empty(df):
        return []
    total = len(df)
    n = total if (limit is None or limit <= 0) else min(total, limit)
    records = []
    for i in range(n):
        row = df.iloc[i] if hasattr(df, "iloc") else df[i]
        if hasattr(row, "index"):
            keys = row.index
        elif isinstance(row, dict):
            keys = row.keys()
        else:
            keys = [k for k in dir(row) if not k.startswith("_")]
        records.append({
            k: to_jsonable(row.get(k) if hasattr(row, "get") else getattr(row, k, None))
            for k in keys
        })
    return records


# ============================================================
# Display Helpers
# ============================================================

def disp_width(s):
    """Return the terminal display width of a string (CJK full-width = 2, others = 1)."""
    from unicodedata import east_asian_width
    return sum(2 if east_asian_width(c) in ("F", "W") else 1 for c in str(s))


def pad_disp(s, width, align="left"):
    """Pad a string to the given display width (CJK-aware)."""
    s = str(s)
    pad = max(0, width - disp_width(s))
    if align == "right":
        return " " * pad + s
    return s + " " * pad


def print_display_df(df, max_colwidth=26):
    """Print a DataFrame to the terminal with CJK-aware column widths."""
    import pandas as pd

    if df is None or is_empty(df):
        print("No data")
        return
    with pd.option_context(
        "display.unicode.east_asian_width", True,
        "display.width", None,
        "display.max_rows", None,
    ):
        print(df.to_string(index=False, max_colwidth=max_colwidth))


def scale_int(value, scale_pow10: int, display_decimals: int = None) -> str:
    """Restore a scaled integer field to a decimal string without floating-point precision loss.

    Example: scale_int(552000000000, 9)    -> "552.000000000"
             scale_int(552000000000, 9, 3) -> "552.000"
             scale_int(35804, 3)           -> "35.804"

    :param value: Raw proto int64 value (int or int-convertible).
    :param scale_pow10: Scale exponent; actual value = value / 10**scale_pow10.
    :param display_decimals: Decimal places to show (defaults to scale_pow10).
    :return: Formatted string with the specified decimal places.
    """
    from decimal import Decimal, ROUND_DOWN
    if value is None:
        return "-"
    try:
        iv = int(value)
    except (TypeError, ValueError):
        return "-"
    d = Decimal(iv)
    divisor = Decimal(10 ** scale_pow10)
    result = d / divisor
    decimals = display_decimals if display_decimals is not None else scale_pow10
    fmt = "0." + "0" * decimals if decimals > 0 else "0"
    return str(result.quantize(Decimal(fmt), rounding=ROUND_DOWN))


def format_big_number(n, *, fixed: int = 2) -> str:
    """Scale a large number to a human-readable string with K/M/B/T suffix.

    Applied consistently across a column when any value is >= 1,000 (JSON path excluded).

    Example: format_big_number(1_500_000_000_000) -> "1.50T"
             format_big_number(2_300_000_000)      -> "2.30B"
             format_big_number(4_500_000)           -> "4.50M"
             format_big_number(12_300)              -> "12.30K"
             format_big_number(999)                 -> "999"

    :param n: Numeric value (int or float).
    :param fixed: Decimal places (default 2).
    :return: Formatted string with suffix.
    """
    if n is None:
        return "-"
    try:
        v = float(n)
    except (TypeError, ValueError):
        return "-"
    import math
    if math.isnan(v) or math.isinf(v):
        return "-"
    abs_v = abs(v)
    if abs_v >= 1e12:
        return f"{v / 1e12:.{fixed}f}T"
    if abs_v >= 1e9:
        return f"{v / 1e9:.{fixed}f}B"
    if abs_v >= 1e6:
        return f"{v / 1e6:.{fixed}f}M"
    if abs_v >= 1e3:
        return f"{v / 1e3:.{fixed}f}K"
    return str(int(v)) if v == int(v) else f"{v:.{fixed}f}"
