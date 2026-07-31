import click
import subprocess
import sys
from pathlib import Path
import shlex
import shutil
from dreemurr.core import generate, DEFAULT_MODEL

def gum_confirm(msg:str) -> bool: # using gum :3
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
        return click.confirm(msg)
    try:
        result = subprocess.run(["gum", "confirm", msg])
        return result.returncode==0
    except FileNotFoundError:
        click.echo("Warning: Gum not installed.")
        return click.confirm(msg)


@click.command
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", help="Confirm changes before writing.", is_flag=True)
def rename(file:Path, model:str, confirm:bool):
    # for i in folder:


    try:
        new = generate(str(file), model=model)
        new += file.suffix
        new_path = file.parent / new

        if confirm and gum_confirm(f"Will rename {file.name} to {new_path}. Proceed?"):
            file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path}.")
        elif not confirm:
            file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path}.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    rename()