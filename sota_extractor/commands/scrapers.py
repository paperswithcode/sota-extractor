import click
from sota_extractor import scrapers
from sota_extractor.consts import Format
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
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def eff(output, fmt):
    """Extract EFF SOTA tables."""
    serialization.dump(tdb=scrapers.eff(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/redditsota.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def reddit(output, fmt):
    """Extract Reddit SOTA tables."""
    serialization.dump(tdb=scrapers.reddit(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/snli.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def snli(output, fmt):
    """Extract SNLI SOTA tables."""
    serialization.dump(tdb=scrapers.snli(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/squad.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def squad(output, fmt):
    """Extract SQUAD SOTA tables."""
    serialization.dump(tdb=scrapers.squad(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/cityscapes.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def cityscapes(output, fmt):
    """Extract Cityscapes SOTA tables."""
    serialization.dump(tdb=scrapers.cityscapes(), output=output, fmt=fmt)


@cli.command("nlp-progress")
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/nlp-progress.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def nlp_progress(output, fmt):
    """Extract NLP Progress SOTA tables."""
    serialization.dump(tdb=scrapers.nlp_progress(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/smcalflow.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def smcalflow(output, fmt):
    """Extract Smcalflow SOTA tables."""
    serialization.dump(tdb=scrapers.smcalflow(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/record.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def record(output, fmt):
    """Extract Record SOTA tables."""
    serialization.dump(tdb=scrapers.record(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/hotpotqa.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def hotpotqa(output, fmt):
    """Extract hotpotqa SOTA tables."""
    serialization.dump(tdb=scrapers.hotpotqa(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/coqa.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def coqa(output, fmt):
    """Extract coqa SOTA tables."""
    serialization.dump(tdb=scrapers.coqa(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/chexpert.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def chexpert(output, fmt):
    """Extract chexpert SOTA tables."""
    serialization.dump(tdb=scrapers.chexpert(), output=output, fmt=fmt)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/xtreme.json",
    help="Output filename.",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(Format),
    default=Format.json,
    help="Output format.",
)
@catch_errors
def xtreme(output, fmt):
    """Extract Xtreme SOTA tables."""
    serialization.dump(tdb=scrapers.xtreme(), output=output, fmt=fmt)
