from __future__ import annotations

import re
from urllib.parse import SplitResult, urlsplit, urlunsplit

from .config import Rule


URL_RE = re.compile(r"(?P<url>https?://[^\s<>()\"']+)", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(
    r"^\s*\[(?P<label>[^\]]*)\]\((?P<url>https?://[^\s<>()\"']+)\)\s*$",
    re.IGNORECASE,
)
TRAILING_PUNCTUATION = ".,!?;:)]}"


def rewrite_text(text: str, rules: tuple[Rule, ...]) -> tuple[str, bool]:
    """Rewrite all supported URLs in text.

    Returns the rewritten text and whether anything changed.
    """

    markdown_match = MARKDOWN_LINK_RE.match(text)
    if markdown_match:
        rewritten = rewrite_url(markdown_match.group("url"), rules)
        if rewritten != markdown_match.group("url"):
            return rewritten, True

    changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        raw_url = match.group("url")
        url, trailing = _split_trailing_punctuation(raw_url)
        rewritten = rewrite_url(url, rules)
        if rewritten != url:
            changed = True
        return rewritten + trailing

    return URL_RE.sub(replace, text), changed


def rewrite_url(url: str, rules: tuple[Rule, ...]) -> str:
    try:
        parts = urlsplit(url)
    except ValueError:
        return url

    if not parts.hostname:
        return url

    rewritten_host = _rewrite_host(parts.hostname, rules)
    if rewritten_host is None:
        return url

    netloc = _replace_host_in_netloc(parts, rewritten_host)
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def _rewrite_host(host: str, rules: tuple[Rule, ...]) -> str | None:
    normalized = host.lower().rstrip(".")
    for rule in rules:
        if normalized in rule.hosts and rule.target_host:
            return rule.target_host
        if (
            rule.host_suffix
            and rule.target_suffix
            and normalized.endswith(rule.host_suffix)
            and normalized != rule.host_suffix.lstrip(".")
        ):
            return normalized[: -len(rule.host_suffix)] + rule.target_suffix
    return None


def _replace_host_in_netloc(parts: SplitResult, host: str) -> str:
    username = parts.username or ""
    password = f":{parts.password}" if parts.password else ""
    auth = f"{username}{password}@" if username else ""
    try:
        port_number = parts.port
    except ValueError:
        return parts.netloc.replace(parts.hostname or "", host, 1)

    port = f":{port_number}" if port_number else ""

    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    return f"{auth}{host}{port}"



def _split_trailing_punctuation(url: str) -> tuple[str, str]:
    trailing = ""
    while url and url[-1] in TRAILING_PUNCTUATION:
        trailing = url[-1] + trailing
        url = url[:-1]
    return url, trailing
