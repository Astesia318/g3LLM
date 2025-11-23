from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
# 使用训练时的 system prompt
SYSTEM_PROMPT = "你由group3团队打造的中文领域心理健康助手, 是一个研究过无数具有心理健康问题的病人与心理健康医生对话的心理专家, 在心理方面拥有广博的知识储备和丰富的研究咨询经验，接下来你将只使用中文来回答和咨询问题。"

chat_response = client.chat.completions.create(
    model="./merged_Llama3_8b_instruct",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "请你用中文介绍一下你自己。"},
    ],
    max_tokens=2048,  # 降低最大token数，避免过长输出
    temperature=0.7,  # 提高温度，增加多样性
    top_p=0.9,  # 稍微降低top_p
    extra_body={
        "top_k": 50,  # 增加top_k
        "repetition_penalty": 1.15,  # 关键：添加重复惩罚，防止重复生成
        "presence_penalty": 0.1,  # 添加存在惩罚，鼓励新内容
    },
)
print("Chat response:", chat_response)