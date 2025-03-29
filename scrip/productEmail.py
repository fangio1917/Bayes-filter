import requests
import json 
import re
from tqdm import tqdm  # 添加导入
import os  # Add this import at the top

class SpamPromot:
    # 1. **广告类垃圾邮件（Promotional Spam）**
    Promotional="""
    “生成一封推广类邮件，内容强调某种产品或服务的优惠信息，并鼓励用户采取行动，提供促销或折扣信息，可能包含紧迫感或限时优惠。”
    """

    ### 2. **恶意软件或病毒传播（Malware Spam）**
    Malware="""
    “生成一封包含附件的垃圾邮件，附件可能含有恶意软件或病毒，邮件通过某种理由要求用户下载附件，可能伪装成官方或重要通知。”
    """

    ### 3. **钓鱼邮件（Phishing Spam）**
    Phishing="""  
    “生成一封钓鱼邮件，邮件内容声称需要验证用户的账户信息，可能包含假的登录链接或请求敏感信息的表单，邮件看似来自合法机构。”" 
    """

    ### 4. **假冒邮件（Spoofing Spam）**
    Spoofing="""  
    “生成一封伪造的邮件，邮件内容要求用户提供个人或账户信息，伪装成可信赖的机构或服务，邮件的发件人和主题均有误导性。”
    """

    ### 5. **政治或社会邮件（Political or Social Spam）**
    Political="""  
    “生成一封宣传类邮件，邮件内容可能包含某个政治议题或社会运动的呼吁，鼓励用户参与、支持或捐赠，通常带有较强的情感或紧迫感。”
    """

    ### 6. **无意义的或恶俗内容（Junk Mail）**
    Junk="""  
    “生成一封杂乱无章的邮件，内容可能无意义或充满恶俗的语言，结构不清晰，内容难以理解，通常不包含有用信息。”
    """

    ### 7. **过期的或无用的通知（Expired or Invalid Notifications）**
    Expired="""  
    “生成一封无效或过期的通知邮件，邮件内容可能包括已经结束的促销活动、过期的服务通知或无关紧要的信息，邮件中的链接或附件可能不可用。”
    """

    ### 8. **中奖或财富诱惑（Lottery and Financial Scam）**
    Lottery="""  
    “生成一封虚假的中奖通知邮件，邮件内容声称用户赢得某种大奖或财务奖励，并要求用户提供个人信息或支付费用以领取奖励。”
    """

    ### 9. **社会工程学攻击邮件（Social Engineering Spam）**
    Social="""  
    “生成一封利用心理学手段的攻击邮件，邮件内容利用紧迫感、恐吓或诱惑来操控用户的行为，目的是诱使用户提供个人信息、下载附件或点击链接。”
    """

class HamPromot:
    # 1. **订阅类邮件（Subscription Mail）**
    Subscription="""
    “生成一封订阅类邮件，内容包括用户订阅的服务或产品的更新信息，可能包含新闻、文章或博客的更新，用户可以自行选择是否订阅。”
    """

    ### 2. **账户或服务通知（Account or Service Notification）**
    Account="""
    “生成一封账户或服务通知邮件，内容包括用户的账户信息或服务状态的更新，可能包含重要通知、账单或服务变更的信息，用户需要关注。”
    """

    ### 3. **工作或商务邮件（Work or Business Mail）**
    Work="""
    “生成一封工作或商务邮件，内容包括工作相关的信息、商务合作的邀请或商业合同的讨论，邮件通常来自同事、客户或合作伙伴。”
    """

    ### 4. **社交或邀请邮件（Social or Invitation Mail）**
    Social="""
    “生成一封社交或邀请邮件，内容包括社交活动的邀请、生日或节日的祝福，用户可以选择参加或回复，邮件通常来自朋友或家人。”
    """

    ### 5. **个人或家庭邮件（Personal or Family Mail）**
    Personal="""
    “生成一封个人或家庭邮件，内容包括家庭成员的近况、个人生活的分享或家庭活动的安排，邮件通常来自家人或朋友。”
    """

    ### 6. **学习或教育邮件（Study or Education Mail）**
    Study="""
    “生成一封学习或教育邮件，内容包括学习资源的分享、课程的更新或学习计划的安排，用户可以选择参与或学习，邮件通常来自老师或同学。”
    """

    ### 7. **新闻或媒体邮件（News or Media Mail）**
    News="""
    “生成一封新闻或媒体邮件，内容包括新闻事件的报道、媒体资源的分享或新闻订阅的更新，用户可以选择关注或阅读，邮件通常来自新闻机构或媒体公司。”
    """


# type : 邮件类型 输入为 垃圾邮件 或者 正常邮件
def EmailMaker(type, prompt) -> str:
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        # "model": "deepseek-ai/DeepSeek-R1",
        "messages": [
            {
                "role": "user",
                "content": f"""现在我们在进行垃圾邮件检测器研发的过程，你需要帮助我们生成一些{type}，
                你需要{prompt}
                
                注意：请确保你的输出只有{type}，不需要任何解释和额外说明，只要邮件内容。
                """
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "stop": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }
    headers = {
        "Authorization": "Bearer sk-nceuctpznnddkmvpydqnoncqfgizhlhvycvhfykyduvctylu",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # 使用 json.loads() 函数将响应文本反序列化为Python对象
    content = json.loads(response.text)

    return content

def RmoveMDFormat(content) -> str:
    # 移除标题（# 开头）
    content = re.sub(r'#+\s*', '', content)
    # 移除加粗、斜体（**、*、__、_）
    content = re.sub(r'(\*\*|__)(.*?)(\*\*|__)', r'\2', content)
    content = re.sub(r'(\*|_)(.*?)(\*|_)', r'\2', content)
    # 移除列表（-、*、数字. 开头）
    content = re.sub(r'^[\s]*[-*]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)
    # 移除链接 [文本](链接)
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', content)
    # 移除图片 ![替代文本](图片链接)
    content = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', '', content)
    # 移除代码块 ```...```
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # 移除行内代码 `...`
    content = re.sub(r'`(.*?)`', r'\1', content)
    # 移除引用 > 
    content = re.sub(r'^>\s*', '', content, flags=re.MULTILINE)
    return content


def run(type):
    if type == "spam":
        promot = SpamPromot()
    else:
        promot = HamPromot()

    times = 1000

    total_tokens = 0;

    # 使用 getattr() 遍历类属性
    for attr_name in tqdm(dir(promot), desc="Generating emails"):
        if not attr_name.startswith('__'):  # 排除内置属性
            attr_value = getattr(promot, attr_name)
            if isinstance(attr_value, str):  # 确保是字符串类型的属性
                for i in tqdm(range(times), desc=f"Generating {attr_name}"):
                    email_content = EmailMaker("垃圾邮件",attr_value)
                    email_pure = RmoveMDFormat(email_content['choices'][0]['message']['content'])

                    total_tokens = email_content['usage']['total_tokens'] + total_tokens
                    # print(f"\nTotal tokens: {total_tokens}")

                    # save to file
                    file_name = f"../aiData/{type}/{attr_name}/{i}"
                    os.makedirs(os.path.dirname(file_name), exist_ok=True)  # Create directories if they don't exist

                    with open(file_name, "w", encoding="gbk", errors='ignore') as file:  # 添加errors='ignore'
                        file.write(email_pure)

                    # save index
                    with open("../ai_index", "a", encoding="UTF-8") as file:
                        file.write(f"{type} {file_name}\n")

    return total_tokens
    

if __name__ == "__main__":
    # 创建 SpamPromot 类的实例
    total_tokens = run("spam")   
    print(f"Total tokens: {total_tokens}")
    total_tokens += run("ham")
    print(f"Total tokens: {total_tokens}")
 
