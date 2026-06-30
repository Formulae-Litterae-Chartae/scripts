#!/usr/bin/env python3
"""
Add verified corpus links to manuscript_siglen.html.

Default input file:
  ~/git/formulae-capitains-nemo/templates/main/manuscript_siglen.html

Default link pattern:
  ../corpus/urn:cts:formulae:<lowercase-siglum>

Only links whose resolved URL answers with HTTP < 400 are inserted.
The Stand date is updated automatically in:
  <p>{{ _('Stand') }} <span id="manuscript-siglen-stand">DD.MM.YY</span></p>

Backups are only created when --backup is passed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

DEFAULT_FILE = "~/git/formulae-capitains-nemo/templates/main/manuscript_siglen.html"
DEFAULT_BASE_URL = "https://werkstatt.formulae.uni-hamburg.de"
DEFAULT_HREF_TEMPLATE = "../corpus/urn:cts:formulae:{siglum}"

DL_RE = re.compile(r"<dl\b[^>]*class=[\"'][^\"']*\brow\b[^\"']*[\"'][^>]*>.*?</dl>", re.DOTALL)
DT_RE = re.compile(r"(?P<open><dt\b[^>]*>)(?P<content>.*?)(?P<close></dt>)", re.DOTALL)
DD_RE = re.compile(r"<dd\b[^>]*>(?P<content>.*?)</dd>|<dd\b[^>]*/\s*>", re.DOTALL)
A_HREF_RE = re.compile(r"<a\b[^>]*\bhref=(?P<quote>[\"'])(?P<href>.*?)(?P=quote)", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
STAND_SPAN_RE = re.compile(
    r"(?P<open><span\b[^>]*\bid=[\"']manuscript-siglen-stand[\"'][^>]*>)"
    r"(?P<date>[^<]*)"
    r"(?P<close></span>)",
    re.DOTALL | re.IGNORECASE,
)


@dataclass
class Issue:
    kind: str
    siglum: str
    label: str
    href: str
    url: str
    reason: str


@dataclass
class Stats:
    linked: int = 0
    already_linked_ok: int = 0
    generated_failed: int = 0
    existing_failed: int = 0
    skipped_without_siglum: int = 0
    stand_updated: bool = False


def visible_text(fragment: str) -> str:
    """Return normalized human-visible text from a small HTML fragment."""
    text = TAG_RE.sub("", fragment)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def siglum_from_dd(dd_content: str) -> str:
    """Extract a compact siglum like P16a from the <dd> fragment."""
    return re.sub(r"\s+", "", visible_text(dd_content))


def href_for_siglum(siglum: str, href_template: str) -> str:
    return href_template.format(siglum=siglum.lower())


def url_for_href(base_url: str, href: str) -> str:
    # Treat the configured base URL as a directory/root, so ../corpus/... resolves predictably.
    return urljoin(base_url.rstrip("/") + "/", href)


def iri_to_uri(url: str) -> str:
    """Percent-encode non-ASCII characters for urllib while keeping the HTML href readable."""
    parts = urlsplit(url)
    netloc = parts.netloc.encode("idna").decode("ascii")
    path = quote(parts.path, safe="/:@")
    query = quote(parts.query, safe="=&?/:;+,%")
    fragment = quote(parts.fragment, safe="")
    return urlunsplit((parts.scheme, netloc, path, query, fragment))


def check_url(url: str, timeout: float, insecure: bool = False) -> tuple[bool, str]:
    """
    Check a URL. Try HEAD first and fall back to a tiny GET because some servers
    do not implement HEAD correctly.
    """
    context: Optional[ssl.SSLContext] = None
    if insecure:
        context = ssl._create_unverified_context()

    encoded_url = iri_to_uri(url)
    headers = {
        "User-Agent": "Formulae manuscript-sigla link checker/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    last_reason = "not checked"
    for method in ("HEAD", "GET"):
        request = Request(encoded_url, headers=headers, method=method)
        if method == "GET":
            request.add_header("Range", "bytes=0-0")
        try:
            with urlopen(request, timeout=timeout, context=context) as response:
                status = response.getcode()
                if status < 400:
                    return True, f"HTTP {status}"
                return False, f"HTTP {status}"
        except HTTPError as exc:
            last_reason = f"HTTP {exc.code}"
            # A HEAD failure may be method-specific; retry with GET.
            if method == "HEAD":
                continue
            return False, last_reason
        except URLError as exc:
            last_reason = str(exc.reason)
            if method == "HEAD":
                continue
            return False, last_reason
        except Exception as exc:  # Keep the batch running even if one URL is malformed.
            last_reason = f"{type(exc).__name__}: {exc}"
            if method == "HEAD":
                continue
            return False, last_reason

    return False, last_reason


def update_stand(text: str, today: str) -> tuple[str, bool]:
    """
    Update the date inside this dedicated metadata element:

      <p>{{ _('Stand') }} <span id="manuscript-siglen-stand">30.06.26</span></p>

    Only the span content is changed. The surrounding markup is left untouched.
    """

    def replacement(match: re.Match[str]) -> str:
        return f"{match.group('open')}{today}{match.group('close')}"

    updated, count = STAND_SPAN_RE.subn(replacement, text, count=1)
    return updated, count > 0


def process_dl_block(
    block: str,
    *,
    base_url: str,
    href_template: str,
    timeout: float,
    insecure: bool,
    stats: Stats,
    issues: list[Issue],
    cache: dict[str, tuple[bool, str]],
) -> str:
    dt_match = DT_RE.search(block)
    dd_match = DD_RE.search(block)
    if not dt_match or not dd_match:
        return block

    dt_content = dt_match.group("content")
    dd_content = dd_match.groupdict().get("content") or ""
    label = visible_text(dt_content)
    siglum = siglum_from_dd(dd_content)

    if not siglum:
        stats.skipped_without_siglum += 1
        return block

    existing_link = A_HREF_RE.search(dt_content)
    if existing_link:
        href = existing_link.group("href")
        url = url_for_href(base_url, href)
        ok, reason = cached_check(url, timeout, insecure, cache)
        if ok:
            stats.already_linked_ok += 1
        else:
            stats.existing_failed += 1
            issues.append(Issue("existing_failed", siglum, label, href, url, reason))
        return block

    href = href_for_siglum(siglum, href_template)
    url = url_for_href(base_url, href)
    ok, reason = cached_check(url, timeout, insecure, cache)
    if not ok:
        stats.generated_failed += 1
        issues.append(Issue("generated_failed", siglum, label, href, url, reason))
        return block

    new_dt = f"{dt_match.group('open')}<a href=\"{href}\">{dt_content}</a>{dt_match.group('close')}"
    stats.linked += 1
    return block[: dt_match.start()] + new_dt + block[dt_match.end() :]


def cached_check(
    url: str,
    timeout: float,
    insecure: bool,
    cache: dict[str, tuple[bool, str]],
) -> tuple[bool, str]:
    if url not in cache:
        cache[url] = check_url(url, timeout=timeout, insecure=insecure)
    return cache[url]


def process_html(
    text: str,
    *,
    base_url: str,
    href_template: str,
    timeout: float,
    insecure: bool,
    today: str,
) -> tuple[str, Stats, list[Issue]]:
    stats = Stats()
    issues: list[Issue] = []
    cache: dict[str, tuple[bool, str]] = {}

    text, stats.stand_updated = update_stand(text, today)

    def replace_block(match: re.Match[str]) -> str:
        return process_dl_block(
            match.group(0),
            base_url=base_url,
            href_template=href_template,
            timeout=timeout,
            insecure=insecure,
            stats=stats,
            issues=issues,
            cache=cache,
        )

    text = DL_RE.sub(replace_block, text)
    return text, stats, issues


def print_report(stats: Stats, issues: list[Issue]) -> None:
    print("\nSummary")
    print("-------")
    print(f"Stand updated: {'yes' if stats.stand_updated else 'no'}")
    print(f"New links inserted: {stats.linked}")
    print(f"Existing links checked and OK: {stats.already_linked_ok}")
    print(f"Generated links not inserted because the URL failed: {stats.generated_failed}")
    print(f"Existing links that failed validation: {stats.existing_failed}")
    print(f"Rows skipped because they have no siglum: {stats.skipped_without_siglum}")

    failed = [issue for issue in issues if issue.kind in {"generated_failed", "existing_failed"}]
    if failed:
        print("\nLinks that could not be generated or validated")
        print("---------------------------------------------")
        for issue in failed:
            prefix = "generated" if issue.kind == "generated_failed" else "existing"
            print(f"- [{prefix}] {issue.siglum}: {issue.label}")
            print(f"  href: {issue.href}")
            print(f"  test: {issue.url}")
            print(f"  reason: {issue.reason}")
    else:
        print("\nAll generated or existing links validated successfully.")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add verified clickable corpus links to manuscript_siglen.html."
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_FILE,
        help=f"HTML/Jinja template to modify. Default: {DEFAULT_FILE}",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL used to test relative links. Default: {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--href-template",
        default=DEFAULT_HREF_TEMPLATE,
        help=(
            "Relative href template. Use {siglum} for the lower-case siglum. "
            f"Default: {DEFAULT_HREF_TEMPLATE}"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout per HTTP request in seconds. Default: 10",
    )
    parser.add_argument(
        "--date",
        default=None,
        help=(
            "Override the date written into the Stand line. "
            "Default: today's date as DD.MM.YY, computed when the script runs."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check and report only; do not write changes.",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a .bak backup before overwriting the file. Default: no backup.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for link checks.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any generated or existing link fails validation.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    path = Path(args.file).expanduser()

    if "{siglum}" not in args.href_template:
        print("ERROR: --href-template must contain {siglum}", file=sys.stderr)
        return 2
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    original = path.read_text(encoding="utf-8")
    updated, stats, issues = process_html(
        original,
        base_url=args.base_url,
        href_template=args.href_template,
        timeout=args.timeout,
        insecure=args.insecure,
        today=args.date or dt.date.today().strftime("%d.%m.%y"),
    )

    if args.dry_run:
        print(f"Dry run: no changes written to {path}")
    elif updated != original:
        if args.backup:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            print(f"Backup written: {backup}")
        path.write_text(updated, encoding="utf-8")
        print(f"Updated file: {path}")
    else:
        print(f"No file changes needed: {path}")

    print_report(stats, issues)

    if args.strict and any(issue.kind in {"generated_failed", "existing_failed"} for issue in issues):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
