import gradio as gr
from openai import OpenAI
from typing import List

# vLLM API 配置
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"
model_name = "./merged_Llama3_8b_instruct"

# 使用训练时的 system prompt
SYSTEM_PROMPT = "你由group3团队打造的中文领域心理健康助手, 是一个研究过无数具有心理健康问题的病人与心理健康医生对话的心理专家, 在心理方面拥有广博的知识储备和丰富的研究咨询经验，接下来你将只使用中文来回答和咨询问题。"

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def chat_with_model(message: str, history: List) -> tuple:
    """
    与模型进行对话
    
    Args:
        message: 用户输入的消息
        history: 对话历史，格式为 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    
    Returns:
        (空字符串, 更新后的对话历史)
    """
    # 如果 history 是元组格式，转换为字典格式
    if history and isinstance(history[0], (tuple, list)) and len(history[0]) == 2:
        # 旧格式: [(user_msg, bot_msg), ...] -> 新格式: [{"role": "user", "content": "..."}, ...]
        messages = []
        for item in history:
            if isinstance(item, (tuple, list)):
                user_msg, bot_msg = item
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})
        history = messages
    elif not history:
        history = []
    
    # 构建发送给 API 的消息列表（包含 system prompt、历史对话和当前用户消息）
    # 如果 history 为空或者是第一次对话，添加 system prompt
    if not history or (len(history) > 0 and history[0].get("role") != "system"):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": message}]
    else:
        messages = history + [{"role": "user", "content": message}]
    
    try:
        # 调用 vLLM API
        chat_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=2048,  # 降低最大token数，避免过长输出
            temperature=0.7,  # 提高温度，增加多样性
            top_p=0.9,  # 稍微降低top_p
            extra_body={
                "top_k": 50,  # 增加top_k
                "repetition_penalty": 1.15,  # 关键：添加重复惩罚，防止重复生成
                "presence_penalty": 0.1,  # 添加存在惩罚，鼓励新内容
            },
        )
        
        # 提取模型回复
        bot_response = chat_response.choices[0].message.content
        
        # 更新对话历史（使用字典格式）
        # 注意：history 已经包含了之前的对话，只需要添加当前这一轮
        updated_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": bot_response}
        ]
        
        return "", updated_history
    
    except Exception as e:
        error_msg = f"错误: {str(e)}"
        updated_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_msg}
        ]
        return "", updated_history


def clear_chat():
    """清空对话历史"""
    return []


# 创建 Gradio 界面
with gr.Blocks(title="g3LLM 心理咨询机器人") as demo:
    gr.Markdown(
        """
        # 🧠 g3LLM 心理咨询机器人
        
        欢迎使用由 Group3 团队打造的中文领域心理健康助手。本助手是一个研究过无数具有心理健康问题的病人与心理健康医生对话的心理专家，在心理方面拥有广博的知识储备和丰富的研究咨询经验。
        
        **模型**: `g3LLM - 心理健康助手`
        
        **功能特点**:
        - 🎯 专业的心理咨询服务
        - 💬 多轮对话支持
        - 🌟 基于 Llama3-8B-Instruct 微调
        - 🔒 安全、私密的对话环境
        """
    )
    
    chatbot = gr.Chatbot(
        label="心理咨询对话窗口",
        height=500,
        placeholder="在这里开始您的心理咨询对话..."
    )
    
    with gr.Row():
        msg = gr.Textbox(
            label="请输入您的问题或困扰",
            placeholder="例如：我最近总是感到很焦虑，尤其是在学业上...",
            scale=4,
            container=False,
        )
        submit_btn = gr.Button("发送", variant="primary", scale=1)
    
    with gr.Row():
        clear_btn = gr.Button("清空对话", variant="secondary")
    
    # 绑定事件
    msg.submit(chat_with_model, [msg, chatbot], [msg, chatbot])
    submit_btn.click(chat_with_model, [msg, chatbot], [msg, chatbot])
    clear_btn.click(clear_chat, None, [chatbot])
    
    gr.Markdown(
        """
        ---
        ### 📖 使用说明
        
        - 💡 **开始对话**: 在输入框中描述您的问题或困扰，然后点击"发送"按钮或按 Enter 键
        - 🔄 **多轮对话**: 支持连续多轮对话，可以深入探讨您的问题
        - 🗑️ **清空对话**: 点击"清空对话"按钮可以清除所有对话历史，开始新的咨询
        - ⚠️ **重要提示**: 
          - 本助手仅提供心理咨询建议，不能替代专业心理医生的诊断和治疗
          - 如遇紧急情况，请及时寻求专业医疗帮助
          - 确保 vLLM 服务正在运行在 `http://localhost:8000`
        
        ---
        **关于 g3LLM**: 由 Group3 团队基于 Llama3-8B-Instruct 模型微调开发的心理健康助手
        """
    )


if __name__ == "__main__":
    # 启动 Web 界面
    # share=True 可以创建一个公共链接（可选）
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,        # 默认端口
        share=False,             # 设置为 True 可以创建公共链接
    )

