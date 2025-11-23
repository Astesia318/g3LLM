import time
from typing import Dict, Any,List, Optional
import os
import json
import asyncio
import random
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from autogen_agentchat.teams import GraphFlow,DiGraphBuilder

from config import *
filename="./dataset/data.jsonl"

class gemini_config:
    api_key="Your_api_key"#替换为你的api_key
    model="gemini-2.5-flash"

model_client = OpenAIChatCompletionClient(
    model=gemini_config.model,
    model_info=ModelInfo(vision=True, function_calling=True, json_output=True, family="unknown", structured_output=True),
    api_key=gemini_config.api_key,
    temperature=0.85
)

async def save_dataset_to_json(
    dialogue_data: List[Dict[str, Any]],
    scores: Dict[str, int], # <--- 新增参数
    scenario: Optional[str] = "unknown"
) -> Dict[str, Any]:
    """
    将生成的、已评估的对话（作为JSON Lines）追加到指定文件中。
    
    Args:
        dialogue_data (List[Dict[str, Any]]): 
            由Agent生成的对话数据列表。
        scores (Dict[str, int]): 
            由Evaluator Agent生成的评分字典。
        scenario (Optional[str]): 
            对话的场景标签。

    Returns:
        Dict[str, Any]: 包含操作状态和文件路径的字典。
    """
    if not dialogue_data or not isinstance(dialogue_data, list):
        return {
            "status": "FAIL",
            "reason": "InvalidData",
            "details": "传入的 'dialogue_data' 必须是一个非空的列表。"
        }
    if not scores or not isinstance(scores, dict):
         return {
            "status": "FAIL",
            "reason": "InvalidData",
            "details": "传入的 'scores' 必须是一个字典。"
        }
    
    try:
        # 将所有信息封装到一个条目中
        entry = {
            "scenario": scenario,
            "scores": scores,
            "dialogue": dialogue_data
        }

        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        line_to_append = json.dumps(entry, ensure_ascii=False)

        with open(filename, 'a', encoding='utf-8') as f:
            f.write(line_to_append + '\n')
        
        print(f"--- 工具执行成功: 已评估的数据 (Scenario: {scenario}, Scores: {scores}) 已追加到 {os.path.abspath(filename)} ---")
        return {
            "status": "SUCCESS",
            "action": "APPENDED_WITH_SCORES",
            "file_path": os.path.abspath(filename),
            "scenario": scenario
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "reason": "UnknownError",
            "details": f"发生未知错误: {str(e)}"
        }

gen_dataset_agent = AssistantAgent(
    name="gen_dataset_agent",
    model_client=model_client,
    tools=[],
    system_message=COUNSELING_DATASET_GENERATOR_SYSTEM_MESSAGE+real_world_data
    
)
evaluator_agent = AssistantAgent(
    name="evaluator_agent",
    model_client=model_client,
    tools=[save_dataset_to_json],
    system_message=EVALUATOR_SYSTEM_MESSAGE+real_world_data
)

async def main():
    builder = DiGraphBuilder()
    builder.add_node(gen_dataset_agent).add_node(evaluator_agent)
    builder.add_edge(gen_dataset_agent,evaluator_agent)
    flow = GraphFlow(builder.get_participants(), graph=builder.build())
    for i in range(n):
        template = random.choice(task_templates)
        total_turns = random.randint(min_turns, max_turns) * 2
        client_turns = total_turns // 2

        task = f"""
        请生成一个{template['description']}的对话，
        共 {total_turns} 轮 ({client_turns}轮Client, {client_turns}轮Counselor)。
        场景标签为'{template['scenario_tag']}'。
        {template['instructions']}
        """

        stream=flow.run_stream(task=task)
        await Console(stream)

        await flow.reset()

asyncio.run(main())