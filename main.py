"""CLI entry point for the local career agent."""

import typer

app = typer.Typer(
    name="career-agent",
    help="Local, privacy-first career agent for ATS-tailored resumes and cover letters.",
)


@app.command()
def info():
    """Display project status and scaffolding info."""
    typer.echo("Resume Builder CLI scaffold initialized.")


if __name__ == "__main__":
    app()

