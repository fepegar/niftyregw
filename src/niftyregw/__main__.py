"""Typer CLI for all NiftyReg binaries."""

import typer

from niftyregw.commands.aladin import aladin
from niftyregw.commands.average import app as average_app
from niftyregw.commands.f3d import f3d
from niftyregw.commands.install import install
from niftyregw.commands.jacobian import jacobian
from niftyregw.commands.measure import measure
from niftyregw.commands.resample import resample
from niftyregw.commands.tools import tools
from niftyregw.commands.transform import app as transform_app

app = typer.Typer(add_completion=False, no_args_is_help=True)

app.command(
    "install",
    help="Download and install NiftyReg binaries.",
)(install)

app.command(
    "aladin",
    help="Block-matching global (affine/rigid) registration.",
    no_args_is_help=True,
)(aladin)
app.command(
    "f3d",
    help="Fast Free-Form Deformation (F3D) non-rigid registration.",
    no_args_is_help=True,
)(f3d)
app.command(
    "measure", help="Compute similarity measures between images.", no_args_is_help=True
)(measure)
app.command(
    "jacobian",
    help="Compute Jacobian-based maps from transformations.",
    no_args_is_help=True,
)(jacobian)
app.command(
    "resample",
    help="Resample an image with a given transformation.",
    no_args_is_help=True,
)(resample)
app.command("tools", help="Image manipulation tools.", no_args_is_help=True)(tools)
app.add_typer(average_app, name="average")
app.add_typer(transform_app, name="transform")


if __name__ == "__main__":
    app()
