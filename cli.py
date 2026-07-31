import click
import subprocess
import sys
from pathlib import Path
import shlex
import shutil
import tempfile
import os
from dreemurr.core import generate, DEFAULT_MODEL

def gum_generate(path:str, model:str) -> str:
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
        click.echo("Generating name...")
        return generate(file, model=model)
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp_path = tmp.name
    try: 
        code = (
            "import sys; "
            "from dreemurr.core import generate; "
            "sys.stdout.write(generate(sys.argv[1], model=sys.argv[2]))"
            )
        cmd = [
            "gum", "spin",
            "--title", "Generating name...",
            "--",
            sys.executable, "-c", code,
            path, model
        ]
        result = subprocess.run(cmd)

        if result.returncode != 0:
            raise RuntimeError("AI name generation failed :(")
        
        with open(tmp_path, "r") as f:
            return f.read().strip()
    finally:
        os.unlink(tmp_path)
    
    return result.stdout.strip()

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
        new = gum_generate(str(file), model)
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