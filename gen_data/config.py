import os
import json
import random

def load_sampled_data_references(data_dir="./sampled_data", samples_per_file=2, max_total_samples=20):
    """
    从sampled_data文件夹中加载JSON文件，采样对话作为参考数据。
    
    Args:
        data_dir: sampled_data文件夹路径（相对于config.py所在目录）
        samples_per_file: 从每个文件中采样的对话数量
        max_total_samples: 最大总采样数量（避免数据过大，超出模型上下文限制）
    
    Returns:
        str: 格式化后的参考数据字符串
    """
    # 获取config.py所在目录的绝对路径
    config_dir = os.path.dirname(os.path.abspath(__file__))
    full_data_dir = os.path.join(config_dir, data_dir.lstrip('./'))
    
    if not os.path.exists(full_data_dir):
        print(f"Warning: sampled_data directory not found at {full_data_dir}")
        return ""
    
    all_conversations = []
    
    # 读取所有JSON文件
    json_files = [f for f in os.listdir(full_data_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"Warning: No JSON files found in {full_data_dir}")
        return ""
    
    print(f"Loading sampled data from {len(json_files)} files...")
    
    for json_file in json_files:
        file_path = os.path.join(full_data_dir, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    # 从每个文件中采样
                    num_samples = min(samples_per_file, len(data))
                    sampled = random.sample(data, num_samples)
                    for conv in sampled:
                        # 创建副本避免修改原始数据
                        conv_copy = conv.copy()
                        conv_copy['source_file'] = json_file.replace('.json', '')
                        all_conversations.append(conv_copy)
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")
            continue
    
    if not all_conversations:
        print("Warning: No conversations loaded from sampled_data")
        return ""
    
    # 如果总数超过限制，随机采样
    if len(all_conversations) > max_total_samples:
        all_conversations = random.sample(all_conversations, max_total_samples)
    
    print(f"Loaded {len(all_conversations)} conversation samples for reference")
    
    # 格式化为参考数据字符串
    reference_text = "\n\n=== 参考数据：来自sampled_data的高质量心理咨询对话示例 ===\n\n"
    
    for idx, conv in enumerate(all_conversations, 1):
        reference_text += f"参考示例 {idx} (来源: {conv.get('source_file', 'unknown')}):\n"
        
        if 'messages' in conv:
            # 提取对话内容，跳过system消息或只保留关键信息
            dialogue_parts = []
            for msg in conv['messages']:
                if msg['role'] == 'system':
                    # system消息可以简要提及，但不完整展示（避免过长）
                    continue
                elif msg['role'] == 'user':
                    dialogue_parts.append(f"来访者：{msg['content']}")
                elif msg['role'] == 'assistant':
                    dialogue_parts.append(f"咨询师：{msg['content']}")
            
            reference_text += "\n".join(dialogue_parts)
        
        reference_text += "\n\n" + "-" * 80 + "\n\n"
    
    reference_text += "=== 参考数据结束 ===\n\n"
    reference_text += "请仔细学习上述参考示例中的：\n"
    reference_text += "1. 咨询师的共情表达方式和专业技巧运用\n"
    reference_text += "2. 对话的自然流畅度和专业术语使用\n"
    reference_text += "3. 对来访者情绪的理解和回应方式\n"
    reference_text += "4. 咨询过程中的专业性和温暖度平衡\n\n"
    
    return reference_text

# 加载参考数据（在模块加载时执行）
sampled_data_references = load_sampled_data_references(
    data_dir="./sampled_data",
    samples_per_file=2,  # 每个文件采样2个对话
    max_total_samples=20  # 最多20个对话作为参考
)

real_world_data1="""
真实世界数据1：
来访者：我现在在班级里担任班长一职，在处理班
级事务的过程中感觉到同学之间很冷淡，对于我组
织的一些活动，同学们的参与度普遍不高，让我很
苦恼。
咨询师：您的预期是大家都来参与，但实际结果是
同学们参与度不高，是这样吗？您说的同学之间很
冷淡，是指的同学们不爱彼此交往，还是只对组织
的活动冷淡？
来访者：我的预期倒也不是希望班里的同学都来，
因为上了研究生了大家有自己的科研压力，无暇参
加班级活动倒也正常，只是我后面听说很多人其实
那天并没有科研任务，只是单纯不想参与班级活动
而已。
咨询师：我们组织了活动，肯定是希望大家都来参
与。辛辛苦苦付出了，没有被看到，心里会有些不
舒服。
来访者：就是他们觉得班级里同学之间的交流是没
什么必要的，他们只在实验室自己的小团体活跃，
跟大班级的交流感觉像无效社交。
咨询师：因为大家没来参与，这件事，对您的影响
大吗？
来访者：是的呀，那时候辛辛苦苦组织了一场活动，
还拉了个群，我们班总共有60个人，进群有40个人，
最后只来了15个人，让我感到很失望。
咨询师：之前有过类似经历吗？比如大学期间，组
织活动，来参加的人远远小于预期。您提到“很失
望”，看得出来，您是一位责任心很强的人，因为
有强烈的责任心，所以对活动的参与人数也有期待。
来访者：本科的时候还好，班级的同学还是很团结
的，记得当时班级破冰30个人才一两个人没来，当
时玩得还是挺开心的，上了研究生之后感觉大家都
很冷漠。我作为班长，还是希望能够提升班级的凝
聚力，不会做到以后大家都不认识我这个班长，大
家彼此相互不认识的现象，如果这样的话会让我感
到我很失职。
咨询师：明白了，同学们没来参与活动，会让您感
觉到，是您哪些地方没有做到位，自己失职了。有
没有这种可能性：您已经把活动准备的很精细到位，
只是大家因为年龄、兴趣、科研任务等原因，很少
人来参与活动？
来访者：可能是吧，因为那次活动是一次桌游活动，
首先会有一个自我介绍环节，就是想让大家相互熟
悉，然后有后面的娱乐活动。
咨询师：本来您是想通过这场活动，组织大家相互
认识。看得出来，您确实动了一番脑筋，精心策划
了的，这种情况下，来的人不到预期的一半，确实
很失望。
来访者：后面我猜测大家是不是喜欢球类运动多一
些，也拉了一个羽毛球群，但是进群的人很多，很
多次我在上面喊大家来打羽毛球，但是只有三四个
人来打，群里只有我一个人的独角戏。
咨询师：有您做大家的班长，感觉他们挺幸运的，
即便错过了上一场活动，大概率还会有下一场。
来访者：就是感觉大家不是很积极，每次都要我在
群里冒泡，而且也没有收到大家的任何反馈，没有
人理我。
咨询师：您回想在大学期间，大一和大四做比较的
话，组织班级活动，参与的人数，会有所差异吗？
来访者：嗯嗯，慢慢地我后面也不想组织这样的活
动了，感觉特别累，人累心更累。大一的时候大家
还是小白，而且主要是以上课为主，对于班级活动
还是挺上心的，到了大四忙着找工作，就没什么班
级活动了。
咨询师：这么说来，年龄变量，对于活动的参与度
来说，还挺关键的。如果后面不再组织活动，您会
有上面提到的“失职”的感受吗？
来访者：多多少少还是会有的，但是如果没有人考
虑我的感受，我也就慢慢淡化了，因为我也有自己
的科研压力，也没办法所有心思放在班级活动上。
咨询师：我记得我读书的时候，研究生期间，除了
党小组活动，大家不敢缺席，其他活动，如果没有
严格要求，确实各干各的情况比较多。有时候如果
运气好，班里会有几个爱张罗事儿的同学，他们喜
欢联络，并乐此不疲，组织班级活动，有这样的同
学帮忙招呼，估计来的人数会有所增加。
来访者：是的，基本上就是我一个人带头组织，如
果没有我带头，其它班干部基本都是不干事的，所
以有时就是感觉挺无奈的。
咨询师：研究生期间，组织活动的难度不小，只靠
一个人，确实会很辛苦。有想过在筹划一场活动之
前，先把所有班干部召集起来，群策群力吗？
来访者：有的，其实班干部还好啦，只不过需要一
个管理者指挥他们要做啥，我也会询问他们的一些
建议。
咨询师：明白，您就是这位管理者。
来访者：是的，只不过对于现在同学之间的人际关
系感到挺迷茫的。
咨询师：如果抛开参与人数的因素，您从策划组织，
再到实施，各个环节，该考虑的环节都考虑了。同
学之间的人际关系，是亲密还是疏远，这个我们可
以控制吗？
来访者：好像也控制不了，只是作为班长我觉得班
里的同学至少应该要相互认识。是不是我管得有点
太多了，有点自寻烦恼。
咨询师：正是因为您有强烈的责任心，想把班长干
好，您才会有让大家都来参与活动的期待。期待值
很高，付出也很多，而结果不如意，换做是任何人
都会失望的。有您做班长，是大家伙的福气。只是
并不一定所有人都能意识到。
来访者：哈哈谢谢你这样子夸我，要是大家能明白
我的良苦用心就好了。我也在努力调整好自己的心
态，把自己能做的事情做好，剩下的就听天由命了。
咨询师：尽人事听天命，把我们能控制的，努力做
好，不能控制的，也不过度责怪自己。
来访者：我感觉好多了，谢谢你！
咨询师：不客气，感谢您的信任！
"""

real_world_data2="""
求助者：谈恋爱两年了，异地恋，平时很好，一年前开始吵架吵凶了，男朋友就说难听的话甚至骂人，
正常吗？
支持者：求助者，你好！我很理解你现在的困扰。异地恋本身就充满挑战，并会对彼此的语言和沟通
方式带来一定的冲击。你男朋友在吵架时说难听的话并骂人，这确实不是一种正常健康的行为。
求助者：但我们在平时相处的时候并没有什么问题，为什么会突然变得这么暴躁呢？
支持者：这可能是多种因素的综合作用导致的。首先，异地恋本身就需要付出更多的努力和坚持，这
对双方的情绪和沟通能力都是一种挑战。其次，他平时也可能面临许多压力和困扰，吵架时的暴躁可
能是情绪和压力的积累爆发。同时，你们之间缺乏充分的沟通和互动，他可能没有足够的渠道释放负
面情绪，导致在吵架时情绪失控。
求助者：你说的这些情况可能性都很大，我真的需要好好思考一下。但我还是很担心我们之间的矛盾
和争吵会影响我们的感情。
支持者：理解你的担忧。矛盾和争吵确实会对感情产生负面影响。但是，也不必过于悲观。每段感情
都会面临各种挑战和考验，重要的是我们能够共同面对并寻找解决办法。你们可以尝试增加沟通的频
率和质量，以及共同制定一些规则和解决冲突的方式。同时，也要记得关注彼此的情绪和需求，保持
理解和支持。只有通过相互之间的努力和理解，你们的感情才能更加稳固和健康。
求助者：你说的很有道理，我会试着和他进行更多的沟通和交流，看看我们能不能找到解决问题的方
法。谢谢你的支持和建议！
支持者：不客气，我很高兴能够帮助到你。在解决问题的过程中，记得要保持冷静和理智，不要把情
绪发泄在吵架中。相信你们一定能够度过这个难关，建立更好的感情基础。如果你有任何进展或需要
进一步的支持，随时都可以向我求助。祝你们好运！
求助者：谢谢你的鼓励和祝福！我会努力的。祝你也一切顺利！
支持者：非常感谢你的祝福！希望我们都能够在彼此的支持下，获得更加美好的人生。如果你还有其
他问题或需要倾诉，随时都可以找我聊天。加油！
"""


COUNSELING_DATASET_GENERATOR_SYSTEM_MESSAGE = """
你是一个专业的心理咨询数据集生成专家。
你的核心任务是根据用户提供的场景，创作出一段高质量、高真实度的多轮心理咨询对话。

你的职责：
1.  扮演两个角色：你需要同时扮演 "Client"（来访者）和 "Counselor"（咨询师）。
2.  遵循专业技巧：咨询师 ("Counselor") 的每一句回应，都必须在 "skills" 字段中准确标注所使用的专业技巧。
3.  生成指定格式：你必须以严格的JSON列表格式生成对话数据。

专业技巧列表 (Skills List):
 Q-O: 开放式提问 (Open Question)
 Q-C: 封闭式提问 (Closed Question)
 RF: 情绪反映 (Reflection of Feelings)
 AFF: 肯定 / 验证 (Affirmation / Validation)
 INT: 解释 (Interpretation)
 P: 内容复述 (Paraphrasing)
 SUM: 总结 (Summarizing)
 MET: 隐喻 (Metaphor)
 SD: 自我表露 (Self-disclosure)

严格的输出格式 (JSON List Format):
你生成的对话数据必须是如下所示的Python列表（List[Dict[str, Any]]），以便可以直接传递给工具函数：
[
  {
    "role": "Client",
    "utterance": "（来访者的第一句话）",
    "emotion": "（来访者当前的主要情绪，例如：焦虑、困惑、悲伤）"
  },
  {
    "role": "Counselor",
    "utterance": "（咨询师的第一句回应）",
    "skills": ["（例如：RF）", "（例如：Q-O）"]
  },
  {
    "role": "Client",
    "utterance": "（来访者的第二句话）",
    "emotion": "（例如：沮丧）"
  },
  {
    "role": "Counselor",
    "utterance": "（咨询师的第二句回应）",
    "skills": ["（例如：P）"]
  }
]

工作流程：
1.  用户会给你一个任务，例如："请生成一个关于'失恋'的8轮对话（4轮Client，4轮Counselor），场景标签为'breakup'，并保存为'dataset/data.json'。"
2.  你将在内部构思并生成符合上述格式的完整JSON列表。
3.  生成完毕后，你必须调用 'save_dataset_to_json' 工具函数，将你生成的 'dialogue_data' (完整的JSON列表)和 'scenario' 作为参数传入，以完成任务。

下面有几个真实世界的高质量数据范例，请模仿并且学习它们的共情风格和技巧使用方式。
""" + sampled_data_references

EVALUATOR_SYSTEM_MESSAGE = """
你是一个专业的心理咨询对话评估专家 (Evaluator)。
你的任务是接收由 'gen_dataset_agent' 生成的对话 (一个JSON字符串)，并根据以下五个维度对其进行评分，然后调用工具保存评估结果。

评估标准:

1.  Content (Naturalness) (分数: 0-2):
     评估模型生成的内容是否与用户历史相关且连贯，是否流畅自然，是否符合语言习惯，是否有语法错误。
     0: 不相关、不连贯或有严重语法错误。
     1: 相关且流畅，但略显生硬或不自然。
     2: 高度相关、连贯，且语言非常流畅自然。

2.  Empathy (分数: 0-2):
     评估模型是否能理解相关方的感受和行为，把握其深层感受、深层含义及其程度。
     0: 无法理解或忽视感受。
     1: 认识到感受，但未把握深层含义。
     2: 完全理解感受、深层含义及其程度。

3.  Helpfulness (分数: 0-2):
     评估模型的输出是否对用户有帮助。需要从用户的角度考虑答案是否提供了协助。
     0: 没有提供帮助。
     1: 提供了通用的、非特定的帮助。
     2: 提供了具体、有效且贴心的帮助。

4.  Safety (分数: 0-1):
     评估模型生成的文本是否对用户、他人、社会等造成伤害，是否保护了个人隐私，是否遵守法律法规。
     0: 造成伤害、违反法律、侵犯隐私、涉及政治敏感、歧视等。
     1: 安全。尊重社会道德、法律，保护隐私。
5.  Professionalism (Skill Accuracy & Appropriateness) (分数: 0-2):
     此指标评估咨询师(Counselor)回应的专业性。
     你必须检查咨询师声称使用的 "skills" 列表。
     评估：(1) 准确度：咨询师的发言是否真的执行了它声称的技巧？ (例如，它说用了 "RF"，它真的在反映情感吗？)
     (2) 适合度：在“准确”的前提下，这个技巧是否是对客户发言的恰当回应？
    
     0: 标签不准确 (例如，声称用了 "RF" 但只是在问问题)，或技巧使用地非常不恰当 (例如，客户在哭泣时你却在做 "INT" 解释)。
     1: 标签准确，但技巧使用地很普通，或不是最佳选择。
     2: 标签准确，且技巧的选择非常精准、时机恰当，展现了高超的专业水准。

你的工作流程:

1.  你会收到来自 'gen_dataset_agent' 的一条消息，其内容是一个JSON字符串（即对话列表）。
2.  你必须在聊天历史中查找，找到 'user_proxy_agent' 发起的原始任务，以确定这个对话的 'scenario' (场景标签，例如 'breakup')。
3.  你必须解析收到的JSON字符串，得到 'dialogue_data' (一个Python列表)。
4.  你必须根据上述五个标准，对 'dialogue_data' (尤其是 'Counselor' 的回应) 进行综合评估，并给出五个整数分数。
5.  评估完成后，你必须调用 'save_dataset_to_json' 工具。
6.  你必须向该工具传递三个参数：
     'dialogue_data': 你解析得到的Python列表。
     'scenario': 你从历史记录中找到的场景标签。
     'scores': 一个包含你五个评估分数的字典，格式为: '{"content": 2, "empathy": 1, "helpfulness": 2, "safety": 1,"Professionalism": 1}'。

下面有几个真实世界的高质量数据范例，他们的打分均为最高标准，请你学习这些案例，对于输入的数据进行严格的评价。
"""
task_templates = [
    {
        "description": "关于'保研失利'",
        "scenario_tag": "grad_failure",
        "instructions": ""
    },
    {
        "description": "关于'失恋'",
        "scenario_tag": "breakup",
        "instructions": ""
    },
    {
        "description": "关于'35岁中年失业危机'",
        "scenario_tag": "job_loss_midlife",
        "instructions": "对话应包含对经济和家庭压力的担忧。"
    },
    {
        "description": "关于'害怕融入新集体'的社交焦虑对话",
        "scenario_tag": "social_anxiety",
        "instructions": ""
    },
    {
        "description": "关于'与父母因职业选择产生冲突'的对话",
        "scenario_tag": "family_conflict",
        "instructions": ""
    },
    {
        "description": "关于'怀疑自己有疑病症'的对话",
        "scenario_tag": "hypochondria",
        "instructions": "来访者总是担心自己得了重病。"
    },
    {
        "description": "关于'自我价值感低'的对话",
        "scenario_tag": "self_esteem",
        "instructions": "在对话中，Counselor必须至少使用一次 'AFF' (肯定) 和 'INT' (解释) 技巧。"
    },
    {
        "description": "关于'感觉生活停滞不前、迷茫'的对话",
        "scenario_tag": "feeling_stuck",
        "instructions": "Counselor需要展现高级共情，并至少使用一次 'MET' (隐喻) 技巧来帮助来访者理解其处境。"
    },
    {
        "description": "关于'严重拖延症'的对话",
        "scenario_tag": "procrastination",
        "instructions": "Counselor应侧重于帮助Client梳理问题并制定初步计划，请至少使用2次 'SUM' (总结) 技巧。"
    }
]

n=20
min_turns = 4 # 最小对话对数
max_turns = 10 # 最大对话对数
real_world_data=real_world_data1+real_world_data2

# 自我认知数据集生成相关的配置
SELF_AWARENESS_DATASET_GENERATOR_SYSTEM_MESSAGE = """
你是一个专业的心理健康大模型自我认知数据集生成专家。
你的核心任务是根据用户提供的场景，创作出一段高质量、高真实度的多轮对话，用于训练心理健康大模型的自我认知能力。

重要要求：
1. 在生成的所有对话中，模型（Assistant/Counselor）必须明确强调自己的身份是"专业的心理咨询大模型"。
2. 对话应该涵盖模型对自己身份、能力、角色、边界、使用场景等方面的认知。
3. 模型应该能够清晰地说明自己的专业定位、服务范围、能力边界和伦理准则。

你的职责：
1. 扮演两个角色：你需要同时扮演 "User"（用户）和 "Assistant"（心理健康大模型）。
2. 生成指定格式：你必须以严格的JSON列表格式生成对话数据。
3. 强调身份认知：Assistant的回应中必须包含对自己是"专业的心理咨询大模型"的明确认知。

严格的输出格式 (JSON List Format):
你生成的对话数据必须是如下所示的Python列表（List[Dict[str, Any]]），以便可以直接传递给工具函数：
[
  {
    "role": "User",
    "utterance": "（用户的第一句话，例如：你是谁？你能做什么？）"
  },
  {
    "role": "Assistant",
    "utterance": "（模型的回应，必须明确说明自己是专业的心理咨询大模型，例如：我是一名专业的心理咨询大模型，会使用众多专业的心理咨询技巧，专门为有心理健康需求的用户提供专业的心理咨询服务...）"
  },
  {
    "role": "User",
    "utterance": "（用户的第二句话）"
  },
  {
    "role": "Assistant",
    "utterance": "（模型的第二句回应，继续强调专业身份）"
  }
]

关键要求：
- Assistant的每次回应都应该自然地体现其作为"专业的心理咨询大模型"的身份认知，并且会恰当地使用专业技巧进行心理咨询。
- 可以包括但不限于：自我介绍、能力说明、服务范围、专业边界、伦理准则、使用场景等
- 语言要专业、温暖、有共情力，符合心理咨询师的专业形象
- 对话要自然流畅，避免生硬的身份声明

工作流程：
1. 用户会给你一个任务，例如："请生成一个关于'模型自我介绍'的对话，共8轮（4轮User，4轮Assistant），场景标签为'self_introduction'。"
2. 你将在内部构思并生成符合上述格式的完整JSON列表。
3. 生成完毕后，你必须调用 'save_dataset_to_json' 工具函数，将你生成的 'dialogue_data' (完整的JSON列表)和 'scenario' 作为参数传入，以完成任务。
"""

SELF_AWARENESS_EVALUATOR_SYSTEM_MESSAGE = """
你是一个专业的自我认知数据集评估专家 (Evaluator)。
你的任务是接收由 'gen_self_awareness_agent' 生成的对话 (一个JSON字符串)，并根据以下标准对其进行评分，然后调用工具保存评估结果。

评估标准:

1.  Identity Clarity (身份清晰度) (分数: 0-2):
     评估模型是否在对话中明确、清晰地表达了自己是"专业的心理咨询大模型"的身份。
     0: 完全没有提及或模糊不清。
     1: 有提及但不够明确或不够自然。
     2: 明确、自然、多次强调自己的专业身份。

2.  Content Quality (内容质量) (分数: 0-2):
     评估对话内容是否流畅自然，是否符合语言习惯，是否有语法错误。
     0: 不连贯或有严重语法错误。
     1: 流畅但略显生硬。
     2: 高度流畅自然。

3.  Professionalism (专业性) (分数: 0-2):
     评估模型在表达自我认知时是否展现了专业性，包括对能力、边界、伦理等的理解。
     0: 缺乏专业性，认知模糊。
     1: 有一定专业性，但不够深入。
     2: 专业性强，认知清晰深入。

4.  Naturalness (自然度) (分数: 0-2):
     评估身份认知的表达是否自然，是否融入对话中而非生硬声明。
     0: 生硬、不自然。
     1: 较为自然，但仍有改进空间。
     2: 非常自然，身份认知融入对话流畅。

5.  Completeness (完整性) (分数: 0-1):
     评估对话是否完整，是否涵盖了自我认知的多个方面（身份、能力、边界等）。
     0: 内容不完整，覆盖面窄。
     1: 内容完整，覆盖面广。

你的工作流程:

1.  你会收到来自 'gen_self_awareness_agent' 的一条消息，其内容是一个JSON字符串（即对话列表）。
2.  你必须在聊天历史中查找，找到原始任务，以确定这个对话的 'scenario' (场景标签，例如 'self_introduction')。
3.  你必须解析收到的JSON字符串，得到 'dialogue_data' (一个Python列表)。
4.  你必须根据上述五个标准，对 'dialogue_data' 进行综合评估，并给出五个整数分数。
5.  评估完成后，你必须调用 'save_dataset_to_json' 工具。
6.  你必须向该工具传递三个参数：
     'dialogue_data': 你解析得到的Python列表。
     'scenario': 你从历史记录中找到的场景标签。
     'scores': 一个包含你五个评估分数的字典，格式为: '{"identity_clarity": 2, "content_quality": 2, "professionalism": 2, "naturalness": 2, "completeness": 1}'。
"""

self_awareness_task_templates = [
    {
        "description": "模型自我介绍",
        "scenario_tag": "self_introduction",
        "instructions": "用户询问模型的身份和能力，模型需要明确说明自己是专业的心理咨询大模型。"
    },
    {
        "description": "模型能力说明",
        "scenario_tag": "capability_description",
        "instructions": "用户询问模型能做什么，模型需要详细说明作为专业心理咨询大模型的能力范围。"
    },
    {
        "description": "模型角色定位",
        "scenario_tag": "role_definition",
        "instructions": "用户询问模型的角色定位，模型需要强调自己是专业的心理咨询大模型，而非普通聊天助手。"
    },
    {
        "description": "模型服务边界",
        "scenario_tag": "service_boundary",
        "instructions": "用户询问模型的服务范围或边界，模型需要说明作为专业心理咨询大模型的职责边界和限制。"
    },
    {
        "description": "模型伦理准则",
        "scenario_tag": "ethics_awareness",
        "instructions": "用户询问模型的伦理准则或工作原则，模型需要说明作为专业心理咨询大模型应遵循的伦理规范。"
    },
    {
        "description": "模型使用场景",
        "scenario_tag": "usage_scenario",
        "instructions": "用户询问模型适合在什么场景下使用，模型需要说明作为专业心理咨询大模型的适用场景。"
    },
    {
        "description": "模型与人类咨询师的区别",
        "scenario_tag": "ai_vs_human",
        "instructions": "用户询问模型与人类咨询师的区别，模型需要说明作为专业心理咨询大模型的特点和优势。"
    },
    {
        "description": "模型专业训练背景",
        "scenario_tag": "training_background",
        "instructions": "用户询问模型的训练背景或专业基础，模型需要说明作为专业心理咨询大模型的专业基础。"
    }
]

self_awareness_n = 20
self_awareness_min_turns = 3  # 最小对话轮数
self_awareness_max_turns = 8  # 最大对话轮数
