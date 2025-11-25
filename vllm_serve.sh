#!/bin/bash

# vLLM 部署 Qwen3-8B 的启动脚本
# 解决 GPU 内存不足问题

# 方法1: 降低 GPU 内存利用率（推荐）
# 将利用率从默认的 0.9 降低到 0.7 或 0.8
CUDA_VISIBLE_DEVICES=2 vllm serve ./merged_Llama3_8b_instruct \
    --gpu-memory-utilization 0.4 \
    --max-model-len 8192 \
    --port 8000

# 方法2: 如果方法1还不够，可以进一步降低利用率和序列长度
# vllm serve Qwen/Qwen3-8B \
#     --gpu-memory-utilization 0.6 \
#     --max-model-len 4096 \
#     --port 8000

# 方法3: 指定特定 GPU 设备（如果有多个 GPU）
# CUDA_VISIBLE_DEVICES=0 vllm serve Qwen/Qwen3-8B \
#     --gpu-memory-utilization 0.7 \
#     --max-model-len 8192 \
#     --port 8000

# 方法4: 使用量化（如果模型支持）
# vllm serve Qwen/Qwen3-8B \
#     --gpu-memory-utilization 0.7 \
#     --quantization awq \
#     --max-model-len 8192 \
#     --port 8000

