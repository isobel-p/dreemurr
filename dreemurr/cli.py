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

def gum_generate(path:str, model:str) -> str:
    # handles gum spinner for generate function
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
        click.echo("Generating name...")
        return generate(path, model=model)
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as result:
        result_path = result.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as script:
        script_path = script.name
        script.write(f"""
import sys
import os
import click
sys.path.insert(0, os.getcwd())
from dreemurr.core import generate
with open({repr(result_path)}, 'w') as f:
    f.write(generate(sys.argv[1], model=sys.argv[2]))
        """)
    try:
        cmd = ["gum", "spin", "--title", "Generating name...", "--", sys.executable, script_path, path, model]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            raise RuntimeError(f"code {result.returncode}")
        with open(result_path, "r") as f:
            name = f.read().strip()
            if not name:
                from datetime import datetime
                name = f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_dreemurr"
                click.echo("AI returned empty string. Using fallback.")
            return name
    finally:
        os.unlink(script_path)
        if os.path.exists(result_path):
            os.unlink(result_path)

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
        new = gum_generate(str(file), model)
        new = sanitise(new)
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
        new = gum_generate(str(file), model)
        new = sanitise(new)
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