import os
from openai import OpenAI
from openai import APIStatusError, APIConnectionError, AuthenticationError, RateLimitError




client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    # 发一个最小的聊天请求测试
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # 便宜且足够测试用；也可以改成你常用的模型
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5,
    )
    # 如果能拿到 choices，基本说明成功
    text = resp.choices[0].message.content
    print("✅ OpenAI API 调用成功，返回内容：", repr(text))


except AuthenticationError as e:
    # 身份认证错误，通常是 key 错误/失效
    print("❌ 认证失败（AuthenticationError），请检查 API Key 是否正确或已失效。")
    print("详细信息：", e)


except RateLimitError as e:
    # 说明 Key 有效，但超出额度/限流
    print("⚠️ 调用被限流或配额已用尽（RateLimitError），但 API Key 是有效的。")
    print("详细信息：", e)


except APIConnectionError as e:
    # 网络或连接问题，无法判断 key 是否有效
    print("⚠️ 无法连接到 OpenAI（APIConnectionError），请检查网络或代理。")
    print("详细信息：", e)


except APIStatusError as e:
    # OpenAI 返回的 HTTP 错误，比如 5xx
    print(f"⚠️ OpenAI 返回错误状态码：{e.status_code}")
    print("详细信息：", e)
    # 一般来说，4xx 可能和请求/Key 有关，5xx 多是服务端问题


except Exception as e:
    # 兜底异常
    print("⚠️ 调用 OpenAI API 时出现未知错误：", e)



