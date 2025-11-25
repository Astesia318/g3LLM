#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Sequence


G3LLM_SYSTEM_PROMPT = (
    "你由group3团队打造的中文领域心理健康助手, "
    "是一个研究过无数具有心理健康问题的病人与心理健康医生对话的心理专家, "
    "在心理方面拥有广博的知识储备和丰富的研究咨询经验，"
    "接下来你将只使用中文来回答和咨询问题。"
)

DATASET_ROOT = Path("/root/zzgroup3/xtuner_finetune/dataset")
DEFAULT_EMOLLM = DATASET_ROOT / "emollm.json"
DEFAULT_BASE = DATASET_ROOT / "multiturn_data_merged.json"
DEFAULT_OUTPUT = DATASET_ROOT / "multiturn_data_merged_plus_emollm.json"


def load_conversations(path: Path) -> List[dict]:
    """Load dataset json file whose root is a list of conversations."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"文件 {path} 的根节点必须是列表。")
    return data


def overwrite_system_prompt(conversation: Sequence[dict]) -> None:
    """Replace every system field with the g3LLM prompt."""
    system_replaced = False
    for turn in conversation:
        if "system" in turn:
            turn["system"] = G3LLM_SYSTEM_PROMPT
            system_replaced = True
    if not system_replaced and conversation:
        conversation[0]["system"] = G3LLM_SYSTEM_PROMPT


def normalize_dataset(records: Iterable[dict]) -> List[dict]:
    """Ensure each conversation contains the desired system prompt."""
    normalized = []
    for record in records:
        convo = record.get("conversation")
        if not isinstance(convo, list) or not convo:
            continue
        overwrite_system_prompt(convo)
        normalized.append({"conversation": convo})
    return normalized


def merge_datasets(base: List[dict], extra: List[dict]) -> List[dict]:
    """Merge datasets by simple list concatenation."""
    return base + extra


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 emollm.json 的 system 字段替换为 g3LLM 提示词并合并到现有数据集中。"
    )
    parser.add_argument(
        "--emollm",
        type=Path,
        default=DEFAULT_EMOLLM,
        help=f"emollm.json 路径 (默认: {DEFAULT_EMOLLM})",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=DEFAULT_BASE,
        help=f"已有的多轮对话数据集路径 (默认: {DEFAULT_BASE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"输出文件路径 (默认: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"加载基础数据集: {args.base}")
    base_data = normalize_dataset(load_conversations(args.base))
    print(f"  - 有效对话数量: {len(base_data)}")

    print(f"加载 EmoLLM 数据集: {args.emollm}")
    emollm_data = normalize_dataset(load_conversations(args.emollm))
    print(f"  - 有效对话数量: {len(emollm_data)}")

    merged = merge_datasets(base_data, emollm_data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)

    print("\n合并完成 ✅")
    print(f"  - 新数据集路径: {args.output}")
    print(f"  - 总对话数量: {len(merged)}")


if __name__ == "__main__":
    main()

