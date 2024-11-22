import ollama

chat_messages = [
            {
                "role": "system",
                "content": """You are an expert proficient in HLS algorithm optimization"""
            },
            {
                "role": "user",
                "content": "Who are you"
            }
        ]

res = ollama.chat(model="llama3.1:8b", stream=False, messages=chat_messages, options={"temperature":0.7})
print(res['message']['content'])