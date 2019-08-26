import click
from sota_extractor import scrapers
from sota_extractor import serialization
from sota_extractor.commands.cli import cli
from sota_extractor.errors import catch_errors


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/eff.json",
    help="Output JSON filename to use.",
)
@catch_errors
def eff(output):
    """Extract EFF SOTA tables."""
    serialization.dump(scrapers.eff(), output)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/redditsota.json",
    help="Output JSON filename to use.",
)
@catch_errors
def reddit(output):
    """Extract Reddit SOTA tables."""
    serialization.dump(scrapers.reddit(), output)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/snli.json",
)
@catch_errors
def snli(output):
    """Extract SNLI SOTA tables."""
    serialization.dump(scrapers.snli(), output)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/squad.json",
    help="Output JSON filename to use.",
)
@catch_errors
def squad(output):
    """Extract SQUAD SOTA tables."""
    serialization.dump(scrapers.squad(), output)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/cityscapes.json",
    help="Output JSON filename to use.",
)
@catch_errors
def cityscapes(output):
    """Extract Cityscapes SOTA tables."""
    serialization.dump(scrapers.cityscapes(), output)