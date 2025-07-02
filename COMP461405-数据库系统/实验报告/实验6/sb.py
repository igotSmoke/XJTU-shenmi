import ollama

question = "openGauss 发布了哪些版本？"
SYSTEM_PROMPT = "你作为一个对话 AI 助手，结合上下文信息简练高效地回答用户提出的问题"
USER_PROMPT = f"请回答{question}的问题，不需要额外的无用回答"

response = ollama.chat(
    model = "deepseek-r1",
    messages = [
        {"role": "user", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
)
print(response["message"]["content"])