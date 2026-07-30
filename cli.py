import click
import subprocess
import sys
from pathlib import Path
from dreemurr.core import generate, DEFAULT_MODEL

@click.command
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", default=False, help="Confirm changes before writing.", is_flag=True)
def rename(file:Path, model:str, confirm:bool):
    try:
        new = generate(str(file), model=model)
        new += file.suffix
        new_path = file.parent / new

        if confirm and click.confirm(f"Will rename {file} to {new_path}. Proceed?"):
            file.rename(new_path)
            click.echo("Done.")
        elif not confirm:
            file.rename(new_path)
            click.echo(f"Renamed {file} to {new_path}.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    rename()

