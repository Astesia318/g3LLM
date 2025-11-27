#!/bin/bash

# vLLM 部署 Qwen3-8B 的启动脚本

CUDA_VISIBLE_DEVICES=0 vllm serve ./merged_Llama3_8b_instruct \
    --gpu-memory-utilization 0.7 \
    --max-model-len 8192 \
    --port 8000

