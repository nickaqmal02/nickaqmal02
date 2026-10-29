"""Refresh the profile SVGs with live GitHub stats.

Pattern borrowed from MZaFaRM/MZaFaRM (originally Andrew6rant's design):
SVG cards hold element ids, this script rewrites their text nodes, and a
GitHub Action runs it daily so the profile stays current without manual edits.

Usage:
    USER_NAME=nickaqmal02 ACCESS_TOKEN=ghp_xxx python today.py

Cache: cache/<sha256(username)>.txt tracks per-repo commit counts so lines-of-
code is only recomputed for repositories that actually changed.
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dateutil import relativedelta
from lxml import etree

USER_NAME = os.environ.get("USER_NAME", "nickaqmal02")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
if not ACCESS_TOKEN:
    sys.exit("ACCESS_TOKEN is not set (fine-grained PAT: read user + read repositories).")

HEADERS = {"authorization": f"token {ACCESS_TOKEN}"}
GRAPHQL = "https://api.github.com/graphql"
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / f"{hashlib.sha256(USER_NAME.encode()).hexdigest()}.txt"

OWNER_ID: dict[str, str] = {}
STAT_IDS = (
    "account_age", "commit_data", "repo_data", "star_data",
    "contrib_data", "follower_data", "loc_data", "loc_delta",
)


# ── GraphQL plumbing ────────────────────────────────────────────────────────
def post_with_retry(query: str, variables: dict, retries: int = 4) -> requests.Response:
    for attempt in range(retries):
        try:
            r = requests.post(GRAPHQL, json={"query": query, "variables": variables},
                              headers=HEADERS, timeout=60)
        except (requests.ConnectionError, requests.Timeout):
            if attempt == retries - 1:
                raise
        else:
            if r.status_code < 500 or attempt == retries - 1:
                return r
        time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def gql(name: str, query: str, variables: dict) -> dict:
    r = post_with_retry(query, variables)
    if r.status_code != 200:
        raise RuntimeError(f"{name} failed: HTTP {r.status_code} {r.text[:300]}")
    return r.json()


def user_getter(username: str) -> tuple[dict[str, str], datetime]:
    data = gql("user_getter", """
        query($login: String!) { user(login: $login) { id createdAt } }
    """, {"login": username})["data"]["user"]
    created = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
    return {"id": data["id"]}, created


def follower_getter(username: str) -> int:
    data = gql("follower_getter", """
        query($login: String!) { user(login: $login) { followers { totalCount } } }
    """, {"login": username})
    return int(data["data"]["user"]["followers"]["totalCount"])


def repo_stats(count_type: str, affiliations: list[str]) -> int:
    """Count repositories, stars, or contributions across the given affiliations."""
    query = """
    query ($aff: [RepositoryAffiliation], $login: String!, $cursor: String) {
      user(login: $login) {
        repositories(first: 100, after: $cursor, ownerAffiliations: $aff) {
          totalCount
          edges { node { ... on Repository { nameWithOwner stargazers { totalCount } } } }
          pageInfo { endCursor hasNextPage }
        }
      }
    }"""
    total, stars, cursor = 0, 0, None
    while True:
        data = gql("repo_stats", query, {"aff": affiliations, "login": USER_NAME, "cursor": cursor})
        repos = data["data"]["user"]["repositories"]
        if count_type == "repos":
            return int(repos["totalCount"])
        for edge in repos["edges"]:
            stars += edge["node"]["stargazers"]["totalCount"]
        if not repos["pageInfo"]["hasNextPage"]:
            return stars
        cursor = repos["pageInfo"]["endCursor"]


# ── Lines of code (cached per repo) ─────────────────────────────────────────
def recursive_loc(owner: str, repo: str, cursor: str | None = None) -> tuple[int, int, int]:
    query = """
    query ($repo: String!, $owner: String!, $cursor: String, $author: ID!) {
      repository(name: $repo, owner: $owner) {
        defaultBranchRef { target { ... on Commit {
          history(first: 100, after: $cursor, author: {id: $author}) {
            edges { node { additions deletions } }
            pageInfo { endCursor hasNextPage }
          } } } }
      }
    }"""
    added = deleted = commits = 0
    while True:
        data = gql("recursive_loc", query,
                   {"repo": repo, "owner": owner, "cursor": cursor, "author": OWNER_ID["id"]})
        ref = data["data"]["repository"]["defaultBranchRef"]
        if ref is None:  # empty repo
            return 0, 0, 0
        history = ref["target"]["history"]
        for edge in history["edges"]:
            commits += 1
            added += edge["node"]["additions"]
            deleted += edge["node"]["deletions"]
        if not history["pageInfo"]["hasNextPage"]:
            return added, deleted, commits
        cursor = history["pageInfo"]["endCursor"]


def all_repos() -> list[tuple[str, int]]:
    """(nameWithOwner, total commit count) for every repo in the affiliations."""
    query = """
    query ($aff: [RepositoryAffiliation], $login: String!, $cursor: String) {
      user(login: $login) {
        repositories(first: 60, after: $cursor, ownerAffiliations: $aff) {
          edges { node { ... on Repository { nameWithOwner
            defaultBranchRef { target { ... on Commit { history { totalCount } } } } } } }
          pageInfo { endCursor hasNextPage }
        }
      }
    }"""
    out: list[tuple[str, int]] = []
    cursor = None
    while True:
        data = gql("all_repos", query,
                   {"aff": ["OWNER", "COLLABORATOR", "ORGANIZATION_MEMBER"],
                    "login": USER_NAME, "cursor": cursor})
        conn = data["data"]["user"]["repositories"]
        for edge in conn["edges"]:
            node = edge["node"]
            try:
                total = int(node["defaultBranchRef"]["target"]["history"]["totalCount"])
            except (TypeError, KeyError):
                total = 0
            out.append((node["nameWithOwner"], total))
        if not conn["pageInfo"]["hasNextPage"]:
            return out
        cursor = conn["pageInfo"]["endCursor"]


def loc_totals(repos: list[tuple[str, int]]) -> tuple[int, int, int]:
    """Sum additions/deletions/commits using the per-repo cache."""
    cache: dict[str, tuple[int, int, int, int]] = {}
    if CACHE_FILE.exists():
        for line in CACHE_FILE.read_text().splitlines():
            parts = line.split()
            if len(parts) == 5:
                cache[parts[0]] = (int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))

    refreshed: dict[str, tuple[int, int, int, int]] = {}
    for name, total in repos:
        key = hashlib.sha256(name.encode()).hexdigest()
        hit = cache.get(key)
        if hit and hit[0] == total:
            refreshed[key] = hit
            continue
        owner, repo = name.split("/")
        added, deleted, mine = recursive_loc(owner, repo) if total else (0, 0, 0)
        refreshed[key] = (total, mine, added, deleted)
        print(f"  loc: {name:<48} +{added:>8,} -{deleted:>8,} ({mine} commits)")

    CACHE_FILE.write_text("".join(
        f"{k} {v[0]} {v[1]} {v[2]} {v[3]}\n" for k, v in refreshed.items()
    ))

    add = sum(v[2] for v in refreshed.values())
    dele = sum(v[3] for v in refreshed.values())
    commits = sum(v[1] for v in refreshed.values())
    return add, dele, commits


# ── SVG writing ─────────────────────────────────────────────────────────────
def set_text(root: etree._Element, element_id: str, value: object) -> None:
    el = root.find(f".//*[@id='{element_id}']")
    if el is None:
        print(f"  !! missing id in SVG: {element_id}")
        return
    el.text = f"{value:,}" if isinstance(value, int) else str(value)


def account_age(created: datetime) -> str:
    diff = relativedelta.relativedelta(datetime.now(timezone.utc), created)
    bits = []
    if diff.years:
        bits.append(f"{diff.years} yr")
    if diff.months:
        bits.append(f"{diff.months} mo")
    return ", ".join(bits) or f"{diff.days} days"


def svg_overwrite(filename: str, values: dict[str, object]) -> None:
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    for eid in STAT_IDS:
        if eid in values:
            set_text(root, eid, values[eid])
    tree.write(filename, encoding="utf-8", xml_declaration=True)


def read_ids(filename: str) -> dict[str, str]:
    """Current text of every stat node, used as a fallback if a call fails."""
    root = etree.parse(filename, etree.XMLParser(remove_blank_text=False)).getroot()
    out: dict[str, str] = {}
    for eid in STAT_IDS:
        el = root.find(f".//*[@id='{eid}']")
        if el is not None and el.text:
            out[eid] = el.text
    return out


def main() -> None:
    global OWNER_ID
    print(f"refreshing profile card for {USER_NAME}")

    previous = read_ids("dark_mode.svg")
    values: dict[str, object] = {}

    def attempt(label: str, eid: str, fn):
        try:
            return fn()
        except Exception as exc:  # keep yesterday's number rather than blank the card
            print(f"  !! {label} failed: {exc} — keeping {previous.get(eid, '—')!r}")
            return previous.get(eid, "—")

    OWNER_ID, created = user_getter(USER_NAME)
    print(f"  account created {created:%Y-%m-%d}")

    try:
        repos = all_repos()
        print(f"  repositories reachable: {len(repos)}")
        add, dele, my_commits = loc_totals(repos)
        values["commit_data"] = my_commits
        values["loc_data"] = add - dele
        values["loc_delta"] = f"+{add:,} / −{dele:,}"
    except Exception as exc:
        print(f"  !! lines-of-code failed: {exc}")

    values["account_age"] = account_age(created)
    values["repo_data"] = attempt("repos", "repo_data", lambda: repo_stats("repos", ["OWNER"]))
    values["star_data"] = attempt("stars", "star_data", lambda: repo_stats("stars", ["OWNER"]))
    values["contrib_data"] = attempt("contributions", "contrib_data",
                                     lambda: repo_stats("repos", ["OWNER", "COLLABORATOR",
                                                                  "ORGANIZATION_MEMBER"]))
    values["follower_data"] = attempt("followers", "follower_data",
                                      lambda: follower_getter(USER_NAME))

    for theme in ("dark", "light"):
        svg_overwrite(f"{theme}_mode.svg", values)
        print(f"  updated {theme}_mode.svg")

    shown = read_ids("light_mode.svg")
    for eid in STAT_IDS:
        print(f"  {eid:<15} {shown.get(eid, '—')}")


if __name__ == "__main__":
    main()
