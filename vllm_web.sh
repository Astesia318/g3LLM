#!/bin/bash

# vLLM Web 界面启动脚本

echo "正在启动 vLLM Web 对话界面..."
echo "请确保 vLLM 服务已启动在 http://localhost:8000"
echo ""

# 启动 Web 界面
python vllm_web.py

