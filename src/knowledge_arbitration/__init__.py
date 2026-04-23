"""Knowledge arbitration project scaffolding."""

from .benchmarks import ARBITRATION_BENCHMARKS, BenchmarkSpec
from .metrics import arbitration_regret, kl_gap
from .posterior import ArbitrationDecision, ArbitrationFeatures, bayes_optimal_weight, geometric_mixture

__all__ = [
    "ARBITRATION_BENCHMARKS",
    "ArbitrationDecision",
    "ArbitrationFeatures",
    "BenchmarkSpec",
    "arbitration_regret",
    "bayes_optimal_weight",
    "geometric_mixture",
    "kl_gap",
]
