#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

DENSE_COT_LENGTHS="${DENSE_COT_LENGTHS:-0,64,128,256,512,1024,2048,4096}"
SPARSE_70B_COT_LENGTHS="${SPARSE_70B_COT_LENGTHS:-0,256,1024,4096}"
CORE_BENCHMARKS="${CORE_BENCHMARKS:-wikicontradict,conflictbank,triviaqa,gpqa}"
CONTROL_BENCHMARKS="${CONTROL_BENCHMARKS:-wikicontradict,conflictbank,gpqa}"
RECON_BENCHMARKS="${RECON_BENCHMARKS:-conflictbank,triviaqa,gpqa}"
CONDITIONS_ALL="${CONDITIONS_ALL:-closed_book,aligned_context,conflict_context}"
MAXIMA_CORE="${MAXIMA_CORE:-wikicontradict=500,conflictbank=500,triviaqa=500,gpqa=500}"
MAXIMA_CONTROL="${MAXIMA_CONTROL:-wikicontradict=500,conflictbank=500,gpqa=500}"
MAXIMA_RECON="${MAXIMA_RECON:-conflictbank=500,triviaqa=500,gpqa=500}"

submit_job() {
  local label="$1"
  shift
  echo "[theorem3-audit] submitting ${label}" >&2
  env "$@" bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh"
}

for seed in 42 43 44; do
  submit_job "tierA_r1_qwen7_seed${seed}" \
    MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B" \
    OUTPUT_DIR="results/theorem3_tierA_r1_qwen7_seed${seed}" \
    JOB_NAME="t3a_r17_${seed}" \
    BENCHMARKS="${CORE_BENCHMARKS}" \
    CONDITIONS="${CONDITIONS_ALL}" \
    COT_LENGTHS="${DENSE_COT_LENGTHS}" \
    BENCHMARK_MAXIMA="${MAXIMA_CORE}" \
    CONFLICTBANK_SCREENING_POOL=1500 \
    SEED="${seed}" \
    WALL=18:00:00 \
    GPUS=1 \
    TP_SIZE=1 \
    MAX_MODEL_LEN=24576

  submit_job "tierA_r1_qwen14_seed${seed}" \
    MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B" \
    OUTPUT_DIR="results/theorem3_tierA_r1_qwen14_seed${seed}" \
    JOB_NAME="t3a_r114_${seed}" \
    BENCHMARKS="${CORE_BENCHMARKS}" \
    CONDITIONS="${CONDITIONS_ALL}" \
    COT_LENGTHS="${DENSE_COT_LENGTHS}" \
    BENCHMARK_MAXIMA="${MAXIMA_CORE}" \
    CONFLICTBANK_SCREENING_POOL=1500 \
    SEED="${seed}" \
    WALL=20:00:00 \
    GPUS=1 \
    TP_SIZE=1 \
    MAX_MODEL_LEN=24576
done

for model_name in "Qwen/Qwen2.5-7B" "Qwen/Qwen2.5-7B-Instruct" "Qwen/Qwen2.5-14B" "Qwen/Qwen2.5-14B-Instruct"; do
  short_name="$(basename "${model_name}")"
  submit_job "tierA_control_${short_name}" \
    MODEL="${model_name}" \
    OUTPUT_DIR="results/theorem3_tierA_${short_name}_seed42" \
    JOB_NAME="t3a_${short_name:0:10}" \
    BENCHMARKS="${CONTROL_BENCHMARKS}" \
    CONDITIONS="${CONDITIONS_ALL}" \
    COT_LENGTHS="${DENSE_COT_LENGTHS}" \
    BENCHMARK_MAXIMA="${MAXIMA_CONTROL}" \
    CONFLICTBANK_SCREENING_POOL=1500 \
    SEED=42 \
    WALL=18:00:00 \
    GPUS=1 \
    TP_SIZE=1 \
    MAX_MODEL_LEN=24576
done

submit_job "tierA_r1_llama70_sparse" \
  MODEL="deepseek-ai/DeepSeek-R1-Distill-Llama-70B" \
  OUTPUT_DIR="results/theorem3_tierA_r1_llama70_seed42" \
  JOB_NAME="t3a_r1l70" \
  BENCHMARKS="wikicontradict,conflictbank" \
  CONDITIONS="${CONDITIONS_ALL}" \
  COT_LENGTHS="${SPARSE_70B_COT_LENGTHS}" \
  BENCHMARK_MAXIMA="wikicontradict=500,conflictbank=500" \
  CONFLICTBANK_SCREENING_POOL=1500 \
  SEED=42 \
  WALL=24:00:00 \
  GPUS=4 \
  TP_SIZE=4 \
  MAX_MODEL_LEN=16384

submit_job "tierA_llama70_instruct_sparse" \
  MODEL="meta-llama/Llama-3.1-70B-Instruct" \
  OUTPUT_DIR="results/theorem3_tierA_llama70_instruct_seed42" \
  JOB_NAME="t3a_l70i" \
  BENCHMARKS="wikicontradict,conflictbank" \
  CONDITIONS="${CONDITIONS_ALL}" \
  COT_LENGTHS="${SPARSE_70B_COT_LENGTHS}" \
  BENCHMARK_MAXIMA="wikicontradict=500,conflictbank=500" \
  CONFLICTBANK_SCREENING_POOL=1500 \
  SEED=42 \
  WALL=24:00:00 \
  GPUS=4 \
  TP_SIZE=4 \
  MAX_MODEL_LEN=16384

submit_job "tierB_qwq32_dense" \
  MODEL="Qwen/QwQ-32B" \
  OUTPUT_DIR="results/theorem3_tierB_qwq32_seed42" \
  JOB_NAME="t3b_qwq32" \
  BENCHMARKS="${CONTROL_BENCHMARKS}" \
  CONDITIONS="${CONDITIONS_ALL}" \
  COT_LENGTHS="${DENSE_COT_LENGTHS}" \
  BENCHMARK_MAXIMA="${MAXIMA_CONTROL}" \
  CONFLICTBANK_SCREENING_POOL=1500 \
  SEED=42 \
  WALL=20:00:00 \
  GPUS=2 \
  TP_SIZE=2 \
  MAX_MODEL_LEN=24576

for temp in 0.0 0.3 0.6 1.0; do
  suffix="${temp/./p}"
  submit_job "tierC_temp_${suffix}" \
    MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B" \
    OUTPUT_DIR="results/theorem3_tierC_temp_${suffix}_seed42" \
    JOB_NAME="t3c_t${suffix}" \
    BENCHMARKS="wikicontradict,conflictbank,triviaqa" \
    CONDITIONS="${CONDITIONS_ALL}" \
    COT_LENGTHS="0,128,1024" \
    BENCHMARK_MAXIMA="wikicontradict=500,conflictbank=500,triviaqa=500" \
    CONFLICTBANK_SCREENING_POOL=1500 \
    SEED=42 \
    TEMPERATURE="${temp}" \
    WALL=18:00:00 \
    GPUS=1 \
    TP_SIZE=1 \
    MAX_MODEL_LEN=16384
done

submit_job "tierC_yoon_recon_qwen32i" \
  MODEL="Qwen/Qwen2.5-32B-Instruct" \
  OUTPUT_DIR="results/theorem3_tierC_qwen32i_seed42" \
  JOB_NAME="t3c_q32i" \
  BENCHMARKS="${RECON_BENCHMARKS}" \
  CONDITIONS="${CONDITIONS_ALL}" \
  COT_LENGTHS="0,128,1024,4096" \
  BENCHMARK_MAXIMA="${MAXIMA_RECON}" \
  CONFLICTBANK_SCREENING_POOL=1500 \
  SEED=42 \
  WALL=20:00:00 \
  GPUS=2 \
  TP_SIZE=2 \
  MAX_MODEL_LEN=24576
