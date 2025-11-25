#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

from datasets import load_dataset
from openai import OpenAI
from tqdm import tqdm

from metric import compute_metrics

SYSTEM_PROMPT = (
    "你由group3团队打造的中文领域心理健康助手, "
    "是一个研究过无数具有心理健康问题的病人与心理健康医生对话的心理专家, "
    "在心理方面拥有广博的知识储备和丰富的研究咨询经验，"
    "接下来你将只使用中文来回答和咨询问题。"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 vLLM(OpenAI API 接口) 对模型进行推理并计算指标"
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:8000/v1",
        help="vLLM OpenAI 兼容服务地址",
    )
    parser.add_argument(
        "--api-key",
        default="EMPTY",
        help="OpenAI API Key（vLLM 默认可用任意值）",
    )
    parser.add_argument(
        "--model-name",
        default="./merged_Llama3_8b_instruct",
        help="vLLM 暴露的模型名称",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("./evaluate/data_dir/converted.json"),
        help="评估数据集 JSON 文件",
    )
    parser.add_argument(
        "--split",
        default="train[:1600]",
        help="datasets 支持的 split 表达式",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=256,
        help="生成的最大新 token 数",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="采样温度",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="核采样阈值",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="一次请求的指令数量（1 表示逐条评估）",
    )
    return parser.parse_args()


def load_eval_data(path: Path, split: str) -> Tuple[List[str], List[str]]:
    dataset = load_dataset("json", data_files=str(path), split=split)
    instructions = list(dataset["instruction"])
    references = list(dataset["output"])
    return instructions, references


def generate_responses(
    client: OpenAI,
    model_name: str,
    instructions: List[str],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> List[str]:
    predictions: List[str] = []
    for instruction in tqdm(instructions, desc="Evaluating"):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction},
        ]
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            extra_body={
                "top_k": 50,
                "repetition_penalty": 1.15,
                "presence_penalty": 0.1,
            },
        )
        content = response.choices[0].message.content
        predictions.append(content.strip() if content else "")
        # 输出predictions
    return predictions


def main() -> None:
    args = parse_args()

    client = OpenAI(
        api_key=args.api_key,
        base_url=args.api_base,
    )

    instructions, references = load_eval_data(args.dataset, args.split)
    print(f"载入评估样本: {len(instructions)} 条")

    predictions = generate_responses(
        client=client,
        model_name=args.model_name,
        instructions=instructions,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )

    metrics = compute_metrics((predictions, references))
    print("\n评估结果：")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

