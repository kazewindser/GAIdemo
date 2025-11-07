import os
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# 计算单词数
def count_words(text):
    return len(text.split())

OriginNews = "岩手日報によると、岩手社会保険事務局事務センターと、岩手社会保険事務局の宮古社会保険事務所が、それぞれ、誤って国民年金の被保険者に保険料の納付を促す書類を送付したことを、2日、岩手社会保険事務局が公表した。事務センターは昨年12月2日に、すでに保険料を納付してあった7人の被保険者に対し、督促はがきを送付した。コンピューターへの入力漏れが原因だった。宮古社会保険事務所では、今年2月20日に、対象外の被保険者269名に対し、保険料の口座振替を勧める文書を送付した。いずれも、書類が届いた被保険者からの指摘によって判明した。岩手社会保険事務局は、社会保険庁の地方社会保険事務局のひとつで、盛岡市、宮古市など岩手県内5カ所に社会保険事務所を置いている。"

PROMPT = (
	"以下是一篇日语新闻文章的开头，请根据上下文接着继续写完整的文章"
	"且最后使得总的新闻长度大概在390~410字符数(word数)(注意不是token数，而是字符数,也就是office办公软件 Word 左下角的字符数)"
	"请严格控制字符数，不要生成过长的内容,动词用原型，不要用ですます型。回复的时候不要换行,不要重复已有的原始新闻的内容。"
	"最后一句话不要断掉，要完整，要用句号结尾。\n\n"
	"新闻为：\n\n" + OriginNews)

# 定义字符数要求
target_min_chars = 400  # 最少字符数
target_max_chars = 410  # 最多字符数
max_attempts = 5        # 最大尝试次数
set_max_tokens = 90

def generate_news():
	attempts = 0
	step = 10
	Continue_Try = True
	GenNews = OriginNews
	global set_max_tokens

	while attempts <= max_attempts and Continue_Try:
		completion = client.chat.completions.create(
		    model="gpt-4o",
		    max_tokens = set_max_tokens,
		    messages=[
		        {"role": "system", "content": "You are a helpful assistant that extends Japanese news articles."},
		        {
		            "role": "user",
		            "content": PROMPT
		        }
		    ]
		)
		generated_text = completion.choices[0].message.content
		GenNews = OriginNews + generated_text
		CountWord = len(GenNews)
		attempts +=1

		if target_min_chars <= CountWord <= target_max_chars:
			Continue_Try = False
			print(attempts)
			return GenNews
		elif CountWord > target_max_chars:
			newstep = step + attempts*5
			set_max_tokens -= step

	else:
		print(attempts)
		return GenNews

FinalNews = generate_news()

print(FinalNews)
print("word数："+ str(len(FinalNews)))

# def generate_text_with_dynamic_tokens_gpt4(prompt, min_words=0, max_words=450, max_attempts=5):
#     attempts = 0
#     best_text = ""
#     best_word_count = 0

#     while attempts < max_attempts:
#         attempts += 1
        
#         # 随机选择目标单词数并转换为 approximate token 数
#         target_words = random.randint(min_words, max_words)
        
#         # 生成文本
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that extends news articles."},
#                 # {"role": "user", "content": f"Please expand the following news article to approximately {target_words} words:\n\n{prompt}"}
#                 {"role": "user", "content": f"Please expand the following news article:\n\n{prompt}"}
#             ],
#             temperature=1.2,
#             max_tokens=3000,  # 默认支持长文本
#             top_p=0.95
#         )

#         # 获取生成的内容
#         generated_text = response.choices[0].message.content

#          # 检查生成文本是否为空
#         if not generated_text:
#             print("Generated text is empty. Skipping this attempt.")
#             continue

#         # 计算生成文本的单词数
#         word_count = count_words(generated_text)

#         # 如果生成的文本在目标范围内，则返回
#         if min_words < word_count <= max_words:
#             return generated_text

#         # 如果生成文本太短或太长，记录当前最接近的文本
#         if min_words < word_count and word_count > best_word_count:
#             best_text = generated_text
#             best_word_count = word_count

#     # 如果尝试次数用完，返回最接近的文本
#     return best_text

# prompt = "8日午後1時50分、参議院本会議にて、郵政民営化に関する法案が否決された。投票数233白票（賛成）108青票（反対）125（内、自由民主党造反議員票22）なお、小泉首相は衆議院を解散する意向を自民党役員会にて示し、午後3時からの会議にて正式発表する。"



# generated_text = generate_text_with_dynamic_tokens_gpt4(prompt, min_words=390, max_words=440)

# print("Find a suitable news：")
# print(generated_text)
# print("word数："+ str(count_words(generated_text)))


