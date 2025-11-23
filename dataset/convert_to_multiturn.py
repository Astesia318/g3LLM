#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


SYSTEM_PROMPT = (
    "你是心理健康助手g3LLM，由Group3团队打造。你旨在通过专业心理咨询，协助来访者完成心理诊断。"
    "请充分利用专业心理学知识与咨询技术，一步步帮助来访者解决心理问题。"
)


def read_jsonl(path: Path) -> Iterable[dict]:
    """读取 JSONL 格式文件（每行一个 JSON 对象）。"""
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as err:
                raise ValueError(f"JSON 解析失败（行 {line_no}）: {err}") from err


def read_json_array(path: Path) -> Iterable[dict]:
    """读取 JSON 数组格式文件（整个文件是一个 JSON 数组）。"""
    with path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    yield item
            else:
                # 如果不是数组，尝试作为单个对象处理
                yield data
        except json.JSONDecodeError as err:
            raise ValueError(f"JSON 解析失败: {err}") from err


def extract_text(message: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    从消息字典中提取角色和文本。
    支持多种角色名称：
    - Client/User/user -> 用户
    - Counselor/Assistant/assistant -> 助手
    - system -> 系统提示（返回特殊标记）
    """
    role = message.get("role")
    
    # 角色映射：将不同的角色名称统一
    role_mapping = {
        "Client": "Client",
        "User": "Client",  # User 映射为 Client
        "user": "Client",  # 小写 user 映射为 Client
        "Counselor": "Counselor",
        "Assistant": "Counselor",  # Assistant 映射为 Counselor
        "assistant": "Counselor",  # 小写 assistant 映射为 Counselor
        "system": "system",  # system 消息
    }
    
    if role not in role_mapping:
        return None, None
    
    # 统一角色名称
    normalized_role = role_mapping[role]
    
    # 尝试多种方式获取文本
    text = message.get("utterance")
    if not text:
        text = message.get("content")  # 有些格式使用 content
    if not text:
        text = message.get(role)  # 有些格式直接使用角色名作为key
    if not isinstance(text, str):
        return None, None
    text = text.strip()
    if not text:
        return None, None
    return normalized_role, text


def build_conversation(dialogue: List[dict], use_custom_system: bool = True) -> List[dict]:
    """
    构建多轮对话格式。
    
    Args:
        dialogue: 消息列表
        use_custom_system: 如果为 True，使用自定义的 SYSTEM_PROMPT；如果为 False，使用数据中的 system 消息
    """
    conversation: List[dict] = []
    pending_user: Optional[str] = None
    system_prompt: Optional[str] = None

    for message in dialogue:
        role, text = extract_text(message)
        if not role:
            continue
        
        # 处理 system 消息
        if role == "system":
            if use_custom_system:
                system_prompt = SYSTEM_PROMPT
            else:
                system_prompt = text
            continue
        
        if role == "Client":
            if pending_user:
                pending_user = f"{pending_user}\n{text}"
            else:
                pending_user = text
        else:  # Counselor
            if not pending_user:
                continue
            turn = {"input": pending_user, "output": text}
            # 只在第一轮对话时添加 system prompt
            # 确保所有对话的第一轮都有 system 字段，以保持数据格式一致性
            if not conversation:
                # 如果没有找到 system 消息，使用默认的 SYSTEM_PROMPT
                if system_prompt is None:
                    system_prompt = SYSTEM_PROMPT
                turn["system"] = system_prompt
            conversation.append(turn)
            pending_user = None
    return conversation


def convert(
    input_path: Path,
    output_path: Path,
) -> None:
    """
    将单个jsonl文件转换为多轮对话格式的json文件。
    
    Args:
        input_path: 输入的jsonl文件路径
        output_path: 输出的json文件路径
    """
    results = []
    for record in read_jsonl(input_path):
        dialogue = record.get("dialogue")
        if not isinstance(dialogue, list):
            continue
        conversation = build_conversation(dialogue)
        if conversation:
            results.append({"conversation": conversation})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


def convert_multiple(
    input_paths: List[Path],
    output_path: Path,
    verbose: bool = True,
    use_custom_system: bool = True,
) -> None:
    """
    将多个文件合并并转换为多轮对话格式的json文件。
    支持 JSONL 格式（每行一个 JSON 对象）和 JSON 数组格式。
    
    Args:
        input_paths: 输入的文件路径列表
        output_path: 输出的json文件路径
        verbose: 是否打印处理进度信息
        use_custom_system: 是否使用自定义的 SYSTEM_PROMPT（True）或使用数据中的 system 消息（False）
    """
    results = []
    total_records = 0
    processed_records = 0
    
    for input_path in input_paths:
        if not input_path.exists():
            if verbose:
                print(f"警告: 文件不存在，跳过: {input_path}")
            continue
        
        if verbose:
            print(f"正在处理: {input_path}")
        
        file_records = 0
        
        # 判断文件格式：尝试读取第一行判断是 JSONL 还是 JSON 数组
        try:
            with input_path.open("r", encoding="utf-8") as f:
                first_char = f.read(1)
                f.seek(0)
                is_jsonl = first_char != "["
        except Exception:
            is_jsonl = True  # 默认按 JSONL 处理
        
        # 根据文件格式选择读取方式
        if is_jsonl:
            reader = read_jsonl(input_path)
        else:
            reader = read_json_array(input_path)
        
        for record in reader:
            total_records += 1
            
            # 支持两种数据格式：
            # 1. 包含 "dialogue" 字段的格式
            # 2. 直接包含 "messages" 字段的格式（sampled_data 中的格式）
            dialogue = record.get("dialogue")
            if not dialogue:
                dialogue = record.get("messages")
            
            if not isinstance(dialogue, list):
                continue
            
            conversation = build_conversation(dialogue, use_custom_system=use_custom_system)
            if conversation:
                results.append({"conversation": conversation})
                processed_records += 1
                file_records += 1
        
        if verbose:
            print(f"  从 {input_path.name} 处理了 {file_records} 条有效对话")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    if verbose:
        print(f"\n转换完成!")
        print(f"  总记录数: {total_records}")
        print(f"  有效对话数: {processed_records}")
        print(f"  输出文件: {output_path}")


def main() -> None:
    """
    主函数：合并处理 JSONL 文件和 sampled_data 文件夹中的所有 JSON 文件。
    1. 处理两个 JSONL 文件（data.jsonl 和 self_awareness_data.jsonl）
    2. 处理 sampled_data 文件夹中的所有 JSON 文件
    3. 将所有数据合并到一个输出文件中
    """
    workspace = Path("/root/zzgroup3")
    dataset_dir = workspace / "xtuner_finetune/dataset"
    sampled_data_dir = dataset_dir / "sampled_data"
    output_path = dataset_dir / "multiturn_data_merged.json"
    
    # 收集所有要处理的文件
    all_input_paths = []
    
    # 1. 添加 JSONL 文件（如果存在）
    jsonl_files = [
        dataset_dir / "data.jsonl",
        dataset_dir / "self_awareness_data.jsonl",
    ]
    
    for jsonl_file in jsonl_files:
        if jsonl_file.exists():
            all_input_paths.append(jsonl_file)
            print(f"找到 JSONL 文件: {jsonl_file.name}")
        else:
            print(f"警告: JSONL 文件不存在，跳过: {jsonl_file.name}")
    
    # 2. 添加 sampled_data 文件夹中的 JSON 文件
    if sampled_data_dir.exists():
        json_files = sorted(sampled_data_dir.glob("*.json"))
        if json_files:
            print(f"\n在 {sampled_data_dir} 中找到 {len(json_files)} 个 JSON 文件:")
            for f in json_files:
                print(f"  - {f.name}")
                all_input_paths.append(f)
        else:
            print(f"警告: 在 {sampled_data_dir} 中未找到 JSON 文件")
    else:
        print(f"警告: 文件夹不存在: {sampled_data_dir}")
    
    # 3. 合并处理所有文件
    if all_input_paths:
        print(f"\n开始处理 {len(all_input_paths)} 个文件...")
        convert_multiple(all_input_paths, output_path, verbose=True, use_custom_system=True)
    else:
        print("错误: 未找到任何要处理的文件！")


if __name__ == "__main__":
    main()

