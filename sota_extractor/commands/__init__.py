__all__ = ["cli", "eff", "reddit", "snli", "squad", "evaluate"]

from sota_extractor.commands.cli import cli
from sota_extractor.commands.scrapers import eff, reddit, snli, squad
from sota_extractor.commands.evaluate import evaluate
