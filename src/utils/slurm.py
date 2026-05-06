"""Helpers for small SLURM script generation tasks."""

from __future__ import annotations

from textwrap import dedent


def render_header(
    account: str,
    partition: str,
    job_name: str,
    time_limit: str,
    gpus_per_node: int,
    cpus_per_task: int,
    output_path: str,
) -> str:
    return dedent(
        f"""\
        #!/bin/bash
        #SBATCH -A {account}
        #SBATCH --partition={partition}
        #SBATCH --nodes=1
        #SBATCH --gpus-per-node={gpus_per_node}
        #SBATCH --cpus-per-task={cpus_per_task}
        #SBATCH --time={time_limit}
        #SBATCH -J {job_name}
        #SBATCH -o {output_path}
        """
    )
