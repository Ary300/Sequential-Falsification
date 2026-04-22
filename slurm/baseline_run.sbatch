#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH -J baseline
#SBATCH -o logs/baseline_%j.out

module purge
module load modtree/gpu
module load conda
source activate tts

python src/evaluate.py \
  --benchmark synthetic_demo \
  --methods greedy,majority_vote,self_debug,oracle \
  --n-candidates 16 \
  --output-dir results/baselines
