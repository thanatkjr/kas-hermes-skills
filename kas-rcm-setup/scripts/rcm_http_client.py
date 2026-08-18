#!/usr/bin/env python3
"""
RCM MCP HTTP Client — เรียก Cloudflare MCP Server โดยตรงผ่าน HTTP
ไม่ต้องใช้ mcp SDK (แก้ปัญหา pywin32/pywintypes missing บน Windows)

Usage ใน execute_code:
    from rcm_http_client import RCMClient
    
    client = RCMClient()
    db = client.get_db_info()
    processes = client.list_processes()
    activities = client.get_process_overview("P")
    risks = client.search_risks("ทุจริต")
    activity = client.get_activity("P", "P-UNVS-001")
    risk = client.get_risk_detail("P", "P-UNVS-001.R1")
    rcm = client.get_process_rcm("P", sector_code="ELEC")

หรือรัน standalone:
    python rcm_http_client.py --tool get_db_info
    python rcm_http_client.py --tool list_processes
    python rcm_http_client.py --tool get_process_overview --process P
    python rcm_http_client.py --tool search_risks --query ทุจริต
    python rcm_http_client.py --tool get_activity --process P --activity P-UNVS-001
"""

import json
import os
import re
import time
import urllib.request
import urllib.error
import urllib.parse
import sys
import argparse
from pathlib import Path

# ── Constants ──────────────────────────────────────────────
MCP_URL = "https://rcm-mcp-server.thanatkjr.workers.dev/mcp"
TOKEN_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "mcp-tokens"
TOKEN_FILE = TOKEN_DIR / "rcm.json"

BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Hermes-RCM-Client/1.0"
}


class RCMClient:
    """Lightweight MCP client for RCM Cloudflare Worker — no mcp SDK needed."""
    
    def __init__(self, token_path: str = None, url: str = None):
        self._url = url or MCP_URL
        self._token_path = token_path or str(TOKEN_FILE)
        self._token_data = self._load_token(self._token_path)
        self._token = self._token_data["access_token"]
        self._session_id = None
        self._init_done = False
    
    # ── Token Management ───────────────────────────────────
    def _load_token(self, path: str) -> dict:
        """Load OAuth token dict from Hermes token store."""
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"OAuth token not found at {path}\n"
                f"Please connect MCP rcm first: Settings → MCP → Add rcm server"
            )
        with open(path) as f:
            data = json.load(f)
        if not data.get("access_token"):
            raise ValueError("No access_token in token file — may need re-auth")
        return data

    def _refresh_token(self) -> None:
        """Refresh an expired access_token via the refresh_token grant (public client).

        PITFALL: the /token endpoint sits behind Cloudflare bot detection — a browser
        User-Agent is REQUIRED (urllib's default UA returns HTTP 403 "error code: 1010").
        The client_id (public client, no secret) lives in the sibling *.client.json file.
        """
        rt = self._token_data.get("refresh_token")
        if not rt:
            raise RuntimeError(
                "No refresh_token available — re-auth via Settings → MCP (Remove → Add)"
            )
        client_id = ""
        client_path = Path(self._token_path).with_suffix(".client.json")
        if client_path.exists():
            try:
                with open(client_path) as f:
                    client_id = json.load(f).get("client_id", "") or ""
            except Exception:
                client_id = ""
        token_url = self._url.rstrip("/").replace("/mcp", "/token")
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": rt,
            "client_id": client_id,
        }).encode()
        req = urllib.request.Request(
            token_url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            new = json.loads(resp.read().decode())
        if not new.get("access_token"):
            raise RuntimeError(f"Refresh failed: {json.dumps(new, ensure_ascii=False)[:300]}")
        self._token_data.update(new)
        self._token_data["expires_at"] = time.time() + new.get("expires_in", 3600)
        self._token = new["access_token"]
        with open(self._token_path, "w") as f:
            json.dump(self._token_data, f)
    
    # ── SSE Parsing ────────────────────────────────────────
    @staticmethod
    def _parse_sse(raw: bytes):
        """Parse Server-Sent Events response, return list of JSON event dicts."""
        text = raw.decode(errors="replace")
        events = []
        for match in re.finditer(r'^data:\s*(.+)$', text, re.MULTILINE):
            try:
                events.append(json.loads(match.group(1)))
            except json.JSONDecodeError:
                pass
        return events
    
    # ── Core HTTP Call ─────────────────────────────────────
    def _call(self, method: str, params: dict) -> list:
        """Make a JSON-RPC call to the MCP server over HTTP. Returns parsed SSE events.
        Auto-refreshes the access token once on HTTP 401 (expired token)."""
        for attempt in (1, 2):
            headers = dict(BASE_HEADERS)
            if self._session_id:
                headers["Mcp-Session-Id"] = self._session_id
            headers["Authorization"] = f"Bearer {self._token}"
            
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1
            }
            
            req = urllib.request.Request(
                self._url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    sid = resp.headers.get("mcp-session-id")
                    if sid:
                        self._session_id = sid
                    return self._parse_sse(resp.read())
            except urllib.error.HTTPError as e:
                body = e.read().decode() if e.fp else ""
                if e.code == 401 and attempt == 1:
                    self._refresh_token()
                    continue
                raise RuntimeError(f"HTTP {e.code}: {body[:500]}")
    
    # ── Initialize MCP Session ─────────────────────────────
    def _init_session(self):
        """Initialize MCP session — called automatically on first tool call."""
        if self._init_done:
            return
        self._call("initialize", {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "hermes-rcm-http", "version": "1.0"}
        })
        self._init_done = True
    
    # ── Tool Call Helper ───────────────────────────────────
    def _tool(self, name: str, args: dict) -> dict:
        """Call a tool and return parsed result as dict."""
        self._init_session()
        events = self._call("tools/call", {"name": name, "arguments": args})
        if not events:
            raise RuntimeError("Empty response from MCP server")
        
        evt = events[0]
        if "error" in evt:
            raise RuntimeError(json.dumps(evt["error"], ensure_ascii=False))
        
        content = evt.get("result", {}).get("content", [])
        if not content:
            raise RuntimeError(f"No content in response: {json.dumps(evt, ensure_ascii=False)[:300]}")
        
        text = content[0].get("text", "")
        if not text:
            return {}
        
        return json.loads(text)
    
    # ════════════════════════════════════════════════════════
    #  PUBLIC TOOL METHODS
    # ════════════════════════════════════════════════════════
    
    def get_db_info(self) -> dict:
        """Get database version, update time, and record counts."""
        return self._tool("get_db_info", {})
    
    def list_processes(self) -> list:
        """List all 10 business processes with activity/risk counts."""
        return self._tool("list_processes", {})
    
    def get_process_overview(self, process_code: str) -> list:
        """
        List all activities in one process with codes + names + sector codes.
        
        Args:
            process_code: One of AF, ELC, FA, HR, IC, IT, OP, P, R, SHE
        """
        return self._tool("get_process_overview", {"process_code": process_code})
    
    def search_risks(self, query: str, process_code: str = None, 
                     risk_category: str = None) -> list:
        """
        Search risks by Thai/English keyword.
        
        Args:
            query: Keyword to search (Thai or English)
            process_code: Optional filter by process
            risk_category: Optional filter by category (Fraud Risk, Operational Risk, etc.)
        """
        args = {"query": query}
        if process_code:
            args["process_code"] = process_code
        if risk_category:
            args["risk_category"] = risk_category
        return self._tool("search_risks", args)
    
    def get_activity(self, process_code: str, activity_code: str) -> dict:
        """
        Get full detail of ONE activity: all risks, controls, tests, 
        policies, validations, procedures.
        
        Args:
            process_code: Process code (P, R, IC, etc.)
            activity_code: Activity code (e.g., P-UNVS-001)
        """
        return self._tool("get_activity", {
            "process_code": process_code,
            "activity_code": activity_code
        })
    
    def get_risk_detail(self, process_code: str, risk_code: str) -> dict:
        """
        Get ONE risk with all fields: poison, indicator, validations,
        policies, procedures, report, controls, tests.
        
        Args:
            process_code: Process code
            risk_code: Risk code (e.g., P-UNVS-001.R1)
        """
        return self._tool("get_risk_detail", {
            "process_code": process_code,
            "risk_code": risk_code
        })
    
    def find_activities(self, keywords_activity: list, keywords_person: list = None,
                        keywords_doc: list = None, process_code: str = None,
                        sector_code: str = None, min_facets: int = None) -> dict:
        """
        Search activities by 3-dimensional keyword intersection (activity/person/doc).
        Returns {total_matched, returned, capped, facets_supplied, min_facets, results}.
        Each result: {activity_code, activity_name, process_code, sector_code,
                      facets_hit, score, matched:{activity[],person[],doc[]}}.
        NOTE: capped at 20 results (capped=True when total_matched > returned).
        """
        args = {"keywords_activity": keywords_activity or []}
        if keywords_person:
            args["keywords_person"] = keywords_person
        if keywords_doc:
            args["keywords_doc"] = keywords_doc
        if process_code:
            args["process_code"] = process_code
        if sector_code:
            args["sector_code"] = sector_code
        if min_facets:
            args["min_facets"] = min_facets
        return self._tool("find_activities", args)

    def get_process_rcm(self, process_code: str, sector_code: str) -> dict:
        """
        Get the FULL RCM for ONE process — all activities, risks, controls,
        tests, questions — for UNVS + one client sector.
        
        Args:
            process_code: Process code (P, R, IC, etc.)
            sector_code: Client's sector code (e.g., "FOOD", "ELEC", "TOUR")
                         UNVS activities are always included automatically.
        """
        return self._tool("get_process_rcm", {
            "process_code": process_code,
            "sector_code": sector_code
        })
    
    def close(self):
        """Close the MCP session (optional — sessions auto-expire)."""
        if self._session_id:
            try:
                self._call("close", {})
            except Exception:
                pass
            self._session_id = None
            self._init_done = False


# ════════════════════════════════════════════════════════════
#  CLI for standalone use
# ════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="RCM MCP HTTP Client")
    parser.add_argument("--tool", required=True, 
                        choices=["get_db_info", "list_processes", "get_process_overview",
                                 "search_risks", "get_activity", "get_risk_detail", 
                                 "get_process_rcm"])
    parser.add_argument("--process", help="Process code (P, R, IC, etc.)")
    parser.add_argument("--activity", help="Activity code (e.g., P-UNVS-001)")
    parser.add_argument("--risk", help="Risk code (e.g., P-UNVS-001.R1)")
    parser.add_argument("--query", help="Search keyword")
    parser.add_argument("--sector", help="Sector code for get_process_rcm (e.g., FOOD, ELEC, TOUR)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    
    args = parser.parse_args()
    
    client = RCMClient()
    indent = 2 if args.pretty else None
    
    try:
        if args.tool == "get_db_info":
            result = client.get_db_info()
        elif args.tool == "list_processes":
            result = client.list_processes()
        elif args.tool == "get_process_overview":
            if not args.process:
                print("Error: --process required", file=sys.stderr)
                sys.exit(1)
            result = client.get_process_overview(args.process)
        elif args.tool == "search_risks":
            if not args.query:
                print("Error: --query required", file=sys.stderr)
                sys.exit(1)
            result = client.search_risks(args.query, args.process)
        elif args.tool == "get_activity":
            if not args.process or not args.activity:
                print("Error: --process and --activity required", file=sys.stderr)
                sys.exit(1)
            result = client.get_activity(args.process, args.activity)
        elif args.tool == "get_risk_detail":
            if not args.process or not args.risk:
                print("Error: --process and --risk required", file=sys.stderr)
                sys.exit(1)
            result = client.get_risk_detail(args.process, args.risk)
        elif args.tool == "get_process_rcm":
            if not args.process or not args.sector:
                print("Error: --process and --sector required", file=sys.stderr)
                sys.exit(1)
            result = client.get_process_rcm(args.process, args.sector)
        
        print(json.dumps(result, ensure_ascii=False, indent=indent))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
