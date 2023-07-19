import asyncio
import asyncclick as click


@click.group()
def cli():
    pass


@cli.command()
# @click.option("--count", default=1, help="Number of greetings.")
# @click.option("--name", prompt="Your name", help="The person to greet.")
async def init() -> None:
    """Wizard for create new project"""
    ...


@cli.command()
async def dev() -> None:
    """Start the development daemon"""
