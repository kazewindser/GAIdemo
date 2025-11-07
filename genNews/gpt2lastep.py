# -*- coding: utf-8 -*-
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "rinna/japanese-gpt2-medium"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

def generate_text(model, tokenizer, prompt, length=100):
    input_ids = tokenizer.encode(prompt, return_tensors='pt', padding=True, truncation=True)
    attention_mask = input_ids.ne(tokenizer.pad_token_id).float()
    output = model.generate(
        input_ids=input_ids,
        min_length = length,
        max_length=length + len(input_ids[0]),
        attention_mask=attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=1.0,
        num_return_sequences=1,
    )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return text

prompt = "毎日新聞によると、5月20日に佐賀県唐津市で起きた男児ひき逃げ事件で、佐賀県警察本部は5月24日、唐津市内に住む土木作業員・坂口三之治（さかぐち・さのじ）容疑者（53歳）を業務上過失傷害、並びにひき逃げによる道路交通法違反の容疑で逮捕した。調べに対し坂口容疑者は容疑を認めている。この事件は5月20日夕方、唐津市内の県道で同市内に住む小学5年生の家原毅君（11歳）を坂口容疑者が運転した会社保有の2トントラックではね、毅君を事故発生現場から3キロ離れた山中に放置したとされる事件である。毅君は頭蓋骨骨折などで全治1ヶ月の大けがを負った。日刊スポーツによると、坂口容疑者の勤務していた土木会社の関係者が23日午後8時半ごろ、捜査員に対して坂口容疑者がいること通報し、連絡を受けた捜査員が国道323号上にいた坂口容疑者を逮捕した。"
generated_text = generate_text(model, tokenizer, prompt, length=40)
print("最后一步生成的目标新闻：")
print(generated_text)