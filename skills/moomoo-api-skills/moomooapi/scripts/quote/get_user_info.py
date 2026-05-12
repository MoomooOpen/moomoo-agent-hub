#!/usr/bin/env python3
"""
Get User Info (Quote Permissions)

Function: Query the current user's quote permission level, subscription quota, etc.
Usage: python get_user_info.py

API Limits:
- No special rate limit
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_quote_context,
    safe_close,
)


# Permission level descriptions
QOT_RIGHT_DESC = {
    "N/A": "Unknown",
    "NO": "No permission",
    "BMP": "BMP (Basic Summary)",
    "LV1": "LV1",
    "LV2": "LV2",
    "SF": "SF (Advanced Quote Enabled)",
}

# Permission field -> Display name
QOT_RIGHT_FIELDS = {
    "hk_qot_right": "HK Stocks",
    "us_qot_right": "US Stocks",
    "cn_qot_right": "A-Shares",
    "hk_option_qot_right": "HK Options",
    "hk_future_qot_right": "HK Futures",
    "us_option_qot_right": "US Options",
    "us_future_qot_right": "US Futures",
    "sg_future_qot_right": "SG Futures",
    "jp_future_qot_right": "JP Futures",
}


def get_user_info(output_json=False):
    ctx = None
    try:
        ctx = create_quote_context()
        ret, data = ctx.get_user_info()
        if ret != 0:
            raise RuntimeError(f"Failed to get user info: {data}")

        if output_json:
            print(json.dumps(data, ensure_ascii=False))
        else:
            print("=" * 50)
            print("User Info")
            print("=" * 50)
            print(f"  Nickname:          {data.get('nick_name', 'N/A')}")
            print(f"  User ID:           {data.get('user_id', 'N/A')}")
            print(f"  User Attribute:    {data.get('user_attr', 'N/A')}")
            print(f"  Sub Quota:         {data.get('sub_quota', 'N/A')}")
            print(f"  History KL Quota:  {data.get('history_kl_quota', 'N/A')}")
            print()
            print("  Quote Permissions:")
            for field, label in QOT_RIGHT_FIELDS.items():
                level = data.get(field, "N/A")
                desc = QOT_RIGHT_DESC.get(level, level)
                print(f"    {label:<12} {desc}")
            print("=" * 50)

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"Error: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get user info (quote permissions)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output in JSON format")
    args = parser.parse_args()
    get_user_info(args.output_json)
