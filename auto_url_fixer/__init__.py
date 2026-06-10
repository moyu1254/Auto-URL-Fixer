"""Clipboard URL fixer."""

from .config import Config, Rule, load_config
from .rewriter import rewrite_text

__all__ = ["Config", "Rule", "load_config", "rewrite_text"]

