#!/bin/bash
#SBATCH -A bio260046
#SBATCH --partition=shared
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH -J prepare_benchmarks
#SBATCH -o logs/prepare_benchmarks_%j.out

module purge
module load conda
source activate tts

python src/prepare_data.py \
  --benchmarks humaneval_plus,mbpp_plus,livecodebench_v6,math500 \
  --data-root data
