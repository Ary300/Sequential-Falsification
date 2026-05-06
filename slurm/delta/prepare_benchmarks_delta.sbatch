#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH -J prepare_bench_delta
#SBATCH -o logs/prepare_benchmarks_delta_%j.out

module load python/anaconda3/2.10.0
source /u/adas17/venvs/tts-delta/bin/activate

cd /u/adas17/tts-falsification
python src/prepare_data.py \
  --benchmarks humaneval_plus,mbpp_plus,livecodebench_v6,math500 \
  --data-root data \
  --prefer-pickle \
  --continue-on-error
