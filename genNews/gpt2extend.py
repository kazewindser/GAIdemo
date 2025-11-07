# -*- coding: utf-8 -*-
import random
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "rinna/japanese-gpt2-medium"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

def count_words(text):
    return len(text)

# 计算给定文本的 token 数
def count_tokens(text, tokenizer):
    input_ids = tokenizer.encode(text, return_tensors='pt')
    return len(input_ids[0])

# 生成文本，直到满足 word 数范围的要求
def generate_text_with_dynamic_tokens(model, tokenizer, prompt, min_words=400, max_words=450, max_attempts=10):
    # 使用更自然的段落来估计字符数和 token 数之间的关系
    sample_text = "東京都三鷹市の国立天文台によれば、シュワスマン・ワハマン第3彗星が5月12日に地球に最接近する。この日にかけた時期には肉眼で観測できるかもしれないと期待されている。12日ごろには4～5等星と最も明るくなるが、満月が13日であるため、連休中から8日ごろにかけてが観測に適しているという。また、核が分裂して急に明るくなる可能性もあるという。同天文台では「謎の彗星見えるかな？」キャンペーンを行っている。この彗星は1930年に発見されたものの、半世紀近く行方がわからなくなったこともあり、謎の彗星とも呼ばれた。"
    avg_token_per_word = count_tokens(sample_text, tokenizer) / len(sample_text)

    # 初始设置较宽的 token 范围
    min_tokens = int(min_words * avg_token_per_word * 0.6)  # 宽松估计较低的 token 数
    max_tokens = int(max_words * avg_token_per_word * 1.4)  # 宽松估计较高的 token 数

    attempts = 0
    best_text = ""
    best_word_count = 0

    while attempts < max_attempts:
        attempts += 1

        # 在 min_tokens 和 max_tokens 范围内随机选择一个目标 token 数
        length = random.randint(min_tokens, max_tokens)
        
        # 对提示进行编码
        input_ids = tokenizer.encode(prompt, return_tensors='pt', padding=True, truncation=True)
        attention_mask = input_ids.ne(tokenizer.pad_token_id).float()

        # 生成文本
        output = model.generate(
            input_ids=input_ids,
            max_length=length + len(input_ids[0]),
            min_length=int(length * 0.8),  # 最小长度设为目标长度的 80%
            attention_mask=attention_mask,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=1.0,
            num_return_sequences=1,
        )

        # 解码生成的文本
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

        # 计算生成文本的字符数（word 数）
        word_count = count_words(generated_text)

        # 如果生成的文本在规定范围内，则返回
        if min_words <= word_count <= max_words:
            return generated_text

        # 如果生成的文本不够长，增加 min_tokens
        if word_count < min_words:
            min_tokens += 10  # 增加最小 token 数，使生成文本变长

        # 如果生成的文本过长，减少 max_tokens
        if word_count > max_words:
            max_tokens -= 10  # 减少最大 token 数，使生成文本变短

        # 记录当前最接近要求的生成文本
        if min_words <= word_count and word_count > best_word_count:
            best_text = generated_text
            best_word_count = word_count

    # 超过最大尝试次数，返回当前最佳生成文本
    return best_text

prompt = "東京都三鷹市の国立天文台によれば、シュワスマン・ワハマン第3彗星が5月12日に地球に最接近する。この日にかけた時期には肉眼で観測できるかもしれないと期待されている。12日ごろには4～5等星と最も明るくなるが、満月が13日であるため、連休中から8日ごろにかけてが観測に適しているという。また、核が分裂して急に明るくなる可能性もあるという。同天文台では「謎の彗星見えるかな？」キャンペーンを行っている。この彗星は1930年に発見されたものの、半世紀近く行方がわからなくなったこともあり、謎の彗星とも呼ばれた。"
generated_text = generate_text_with_dynamic_tokens(model, tokenizer, prompt, min_words=380, max_words=420)

print("Find a suitable news：")
print(generated_text)
print("word数："+ str(count_words(generated_text)))

# def generate_text(model, tokenizer, prompt, min_length=100, max_length=200):
#     input_ids = tokenizer.encode(prompt, return_tensors='pt', padding=True, truncation=True)
#     attention_mask = input_ids.ne(tokenizer.pad_token_id).float()

#     output = model.generate(
#         input_ids=input_ids,
#         max_length=max_length  + len(input_ids[0]),
#         min_length=min_length,
#         attention_mask=attention_mask,
#         pad_token_id=tokenizer.eos_token_id,
#         do_sample=True,
#         top_k=50,
#         top_p=0.95,
#         temperature=1.0,
#         num_return_sequences=1,
#     )

#     text = tokenizer.decode(output[0], skip_special_tokens=True)
#     return text


# def generate_text_with_ratio(model, tokenizer, prompt, ratio=0.1):
#     # 计算原始新闻的 token 长度
#     input_ids = tokenizer.encode(prompt, return_tensors='pt')
#     original_length = len(input_ids[0])

#     # 根据比例计算扩写后的目标长度
#     # 如果原始新闻占比是 ratio，则生成后的总长度应为原始长度 / ratio
#     target_length = int(original_length / ratio)

#     # 生成续写文本
#     output = model.generate(
#         input_ids=input_ids,
#         max_length=target_length,
#         attention_mask=input_ids.ne(tokenizer.pad_token_id).float(),
#         pad_token_id=tokenizer.eos_token_id,
#         do_sample=True,
#         top_k=50,
#         top_p=0.95,
#         temperature=1.0,
#         num_return_sequences=1,
#     )

#     # 解码生成的文本
#     generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

#     return generated_text





