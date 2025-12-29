from openai import OpenAI

client = OpenAI(
    base_url='https://api.siliconflow.cn/v1',
    api_key='your-api-key'
)

# 发送带有流式输出的请求
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V2.5",
    messages=[
        {"role": "user", "content": "SiliconFlow公测上线，每用户送3亿token 解锁开源大模型创新能力。对于整个大模型应用领域带来哪些改变？"}
    ],
    stream=True  # 启用流式输出
)

# 逐步接收并处理响应
for chunk in response:
    if not chunk.choices:
        continue
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content, end="", flush=True)

