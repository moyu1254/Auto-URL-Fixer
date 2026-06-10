from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Rule:
    name: str
    enabled: bool
    hosts: tuple[str, ...] = ()
    target_host: str | None = None
    host_suffix: str | None = None
    target_suffix: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        hosts = tuple(str(host).lower() for host in data.get("hosts", ()))
        target_host = _optional_lower(data.get("target_host"))
        host_suffix = _optional_lower(data.get("host_suffix"))
        target_suffix = _optional_lower(data.get("target_suffix"))

        if hosts and not target_host:
            raise ValueError(f"Rule {data.get('name')!r} has hosts but no target_host.")
        if host_suffix and not target_suffix:
            raise ValueError(f"Rule {data.get('name')!r} has host_suffix but no target_suffix.")
        if not hosts and not host_suffix:
            raise ValueError(f"Rule {data.get('name')!r} must define hosts or host_suffix.")

        return cls(
            name=str(data.get("name", "Unnamed rule")),
            enabled=bool(data.get("enabled", True)),
            hosts=hosts,
            target_host=target_host,
            host_suffix=host_suffix,
            target_suffix=target_suffix,
        )


@dataclass(frozen=True)
class Config:
    poll_interval_seconds: float
    log_rewrites: bool
    rules: tuple[Rule, ...]

    @property
    def enabled_rules(self) -> tuple[Rule, ...]:
        return tuple(rule for rule in self.rules if rule.enabled)


def load_config(path: Path | None = None) -> Config:
    if path is None:
        data = _default_config_data()
    else:
        data = json.loads(path.read_text(encoding="utf-8"))

    return Config(
        poll_interval_seconds=float(data.get("poll_interval_seconds", 0.5)),
        log_rewrites=bool(data.get("log_rewrites", True)),
        rules=tuple(Rule.from_dict(rule) for rule in data.get("rules", ())),
    )


def _optional_lower(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).lower()


def _default_config_data() -> dict[str, Any]:
    return {
        "poll_interval_seconds": 0.5,
        "log_rewrites": True,
        "rules": [
            {
                "name": "X / Twitter to FxTwitter",
                "enabled": True,
                "hosts": ["twitter.com", "www.twitter.com", "mobile.twitter.com"],
                "target_host": "fxtwitter.com",
            },
            {
                "name": "X to FixupX",
                "enabled": True,
                "hosts": ["x.com", "www.x.com"],
                "target_host": "fixupx.com",
            },
            {
                "name": "pixiv to phixiv",
                "enabled": True,
                "hosts": ["pixiv.net", "www.pixiv.net"],
                "target_host": "phixiv.net",
            },
            {
                "name": "Instagram to ddinstagram",
                "enabled": True,
                "hosts": ["instagram.com", "www.instagram.com"],
                "target_host": "ddinstagram.com",
            },
            {
                "name": "TikTok to tnktok",
                "enabled": True,
                "hosts": [
                    "tiktok.com",
                    "www.tiktok.com",
                    "m.tiktok.com",
                    "vm.tiktok.com",
                    "vt.tiktok.com",
                ],
                "target_host": "tnktok.com",
            },
            {
                "name": "Reddit to rxddit",
                "enabled": True,
                "hosts": ["reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com"],
                "target_host": "rxddit.com",
            },
            {
                "name": "Tumblr to tpmblr",
                "enabled": True,
                "hosts": ["tumblr.com", "www.tumblr.com"],
                "target_host": "tpmblr.com",
            },
            {
                "name": "Tumblr blog subdomains to tpmblr",
                "enabled": True,
                "host_suffix": ".tumblr.com",
                "target_suffix": ".tpmblr.com",
            },
            {
                "name": "Bluesky to FxBluesky",
                "enabled": True,
                "hosts": ["bsky.app", "www.bsky.app"],
                "target_host": "fxbsky.app",
            },
        ],
    }

