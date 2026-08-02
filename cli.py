import click
import subprocess
import sys
from pathlib import Path
import shlex
import shutil
import tempfile
import os
from dreemurr.core import generate, DEFAULT_MODEL
from dreemurr.utils import sanitise, unique
from yaspin import yaspin

def gum_confirm(msg:str) -> bool:
    # handles gum confirm message when --confirm flag is used
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
        return click.confirm(msg)
    try:
        result = subprocess.run(["gum", "confirm", msg])
        return result.returncode==0
    except FileNotFoundError:
        click.echo("Warning: Gum not installed.")
        return click.confirm(msg)

def rename(file:Path, model:str, confirm:bool) -> bool:
    # rename one file
    try:
        with yaspin(text="Generating name...") as spinner:
            new = sanitise(generate(str(file), model=model))
            spinner.ok()
        new += file.suffix
        new_path = file.parent / new
        new_path = unique(new_path)

        if confirm and gum_confirm(f"Will rename {file.name} to {new_path.name}. Proceed?"):
            file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path.name}.")
        elif not confirm:
            file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path.name}.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

def copy(file:Path, model:str, confirm:bool) -> bool:
    # copy one file
    try:
        with yaspin(text="Generating name...") as spinner:
            new = sanitise(generate(str(file), model=model))
            spinner.ok()
        new += file.suffix
        new_path = file.parent / new
        new_path = unique(new_path)

        if confirm and gum_confirm(f"Will copy {file.name} to {new_path.name}. Proceed?"):
            shutil.copy2(file, new_path)
            click.echo(f"Copied {file.name} to {new_path.name}.")
        elif not confirm:
            shutil.copy2(file, new_path)
            click.echo(f"Copied {file.name} to {new_path.name}.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@click.group()
def cli():
    pass

@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", help="Confirm changes before writing.", is_flag=True)
@click.option("--copy", help="Create a copy with the new name instead of overwriting the old one.", is_flag=True)
def single(file:Path, model:str, confirm:bool, copy:bool):
    # use gum file picker to get file name, renames one file at a time
    if file is None:
        if shutil.which("gum") is None:
            click.echo("Warning: Gum not installed.")
            click.echo("Please install Gum or provide a file path.")
            sys.exit(1)
        result = subprocess.run(["gum", "file", str(Path.home())], stdout=subprocess.PIPE, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            sys.exit(1)
        file_path = result.stdout.strip()
        file = Path(file_path)
        if not file.exists():
            click.echo("File does not exist", err=True)
            sys.exit(1)
    if copy:
        copy(file, model, confirm)
    else:
        rename(file, model, confirm)

def batch(file:Path, model:str, confirm:bool, copy:bool):
    # use gum file picker to get file name, renames one file at a time
    if file is None:
        if shutil.which("gum") is None:
            click.echo("Warning: Gum not installed.")
            click.echo("Please install Gum or provide a file path.")
            sys.exit(1)
        result = subprocess.run(["gum", "file", str(Path.home())], stdout=subprocess.PIPE, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            sys.exit(1)
        file_path = result.stdout.strip()
        file = Path(file_path)
        if not file.exists():
            click.echo("File does not exist", err=True)
            sys.exit(1)
    if copy:
        copy(file, model, confirm)
    else:
        rename(file, model, confirm)


if __name__ == "__main__":
    cli()