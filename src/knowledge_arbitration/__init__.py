"""Knowledge arbitration research scaffolding."""

from .benchmarks import ARBITRATION_BENCHMARKS, BenchmarkSpec
from .experiment import run_benchmark_experiment, run_synthetic_experiment
from .features import ReliabilityFeatures, build_reliability_features
from .loaders import load_arbitration_dataset, normalize_arbitration_example
from .metrics import arbitration_kl_divergence, bayes_regret
from .posterior import (
    ArbitrationFeatures,
    ArbitrationResult,
    bayes_arbitration_probability,
    bayes_arbitration_result,
)
from .synthetic import synthetic_grid

__all__ = [
    "ARBITRATION_BENCHMARKS",
    "ArbitrationFeatures",
    "ArbitrationResult",
    "BenchmarkSpec",
    "ReliabilityFeatures",
    "arbitration_kl_divergence",
    "bayes_arbitration_probability",
    "bayes_arbitration_result",
    "bayes_regret",
    "build_reliability_features",
    "load_arbitration_dataset",
    "normalize_arbitration_example",
    "run_benchmark_experiment",
    "run_synthetic_experiment",
    "synthetic_grid",
]
