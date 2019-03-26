import click
from sota_extractor import scrapers
from sota_extractor.commands.cli import cli


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/eff.json",
    help="Output JSON filename to use.",
)
def eff(output):
    """Extract EFF SOTA tables."""
    try:
        scrapers.eff(output)
    except Exception as e:
        click.secho(str(e), fg="red")


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/redditsota.json",
    help="Output JSON filename to use.",
)
def reddit(output):
    """Extract Reddit SOTA tables."""
    try:
        scrapers.reddit(output)
    except Exception as e:
        click.secho(str(e), fg="red")


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/snli.json",
)
def snli(output):
    """Extract SNLI SOTA tables."""
    try:
        scrapers.snli(output)
    except Exception as e:
        click.secho(str(e), fg="red")


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False),
    required=False,
    default="data/tasks/squad.json",
    help="Output JSON filename to use.",
)
def squad(output):
    """Extract SQUAD SOTA tables."""
    try:
        scrapers.squad(output)
    except Exception as e:
        click.secho(str(e), fg="red")
