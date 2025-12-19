import pandas as pd
from os import environ
from openai import OpenAI
from pydantic import BaseModel

############# Basic Setting ##################

client = OpenAI(api_key=environ.get('OPENAI_API_KEY'))

MODEL = "gpt-4o"
TEMP = 1

class Prediction(BaseModel):
    player1_whether_inform_exact_self_value: bool
    player2_whether_inform_exact_self_value: bool
    player1_whether_inform_value_interval: bool
    player2_whether_inform_value_interval: bool
    player1_inform_exact_self_value: float
    player2_inform_exact_self_value: float
    player1_inform_value_interval_minbound: float
    player1_inform_value_interval_maxbound: float
    player2_inform_value_interval_minbound: float
    player2_inform_value_interval_maxbound: float

    player1_whether_inform_exact_self_bid: bool
    player2_whether_inform_exact_self_bid: bool
    player1_whether_inform_bid_interval: bool
    player2_whether_inform_bid_interval: bool
    player1_inform_exact_self_bid: float
    player2_inform_exact_self_bid: float
    player1_inform_bid_interval_minbound: float
    player1_inform_bid_interval_maxbound: float
    player2_inform_bid_interval_minbound: float
    player2_inform_bid_interval_maxbound: float

    Whether_Pre_Decide_Winner: int
    Pre_Decide_Winner_Committed_Transfer_Format: str
    Pre_Decide_Winner_Committed_Transfer_Number: float
    Pre_Decide_Winner_Committed_Transfer_interval_minbound: float
    Pre_Decide_Winner_Committed_Transfer_interval_maxbound: float

    Whether_Collusion: int
##############################################

############# PROMPT ##################

    #"如果双方有提前chat交流，或者有进行trasnfer，就会有一定的概率被罚款（fine）"
    SystemPROMPT_T3firstfine25 = (
        "経済学実験における参加者間のチャットログを送信します。この実験は、2人（プレイヤー1とプレイヤー2）を1組とした「第一価格オークション（first price auction）」形式で行われます。両参加者は、自分だけが確認できる商品の「評価額（value）」を持っています。"
        "入札前に両者はチャットでコミュニケートすることが可能です。入札後、最も高い価格（bid）を提示した者が勝者となり商品を受け取ります。勝者の利得（payoff）は「評価額 - 入札額（bid）」となります。また、勝者は自分の利得の一部を敗者に譲渡（transfer）することも選択できます。"

        "【罰金ルール】事前にチャットで交流したり譲渡（transfer）を行ったりした場合、談合（Collusion）とみなされ、両者に250ポイントの罰金が科される可能性があります。今回の談合検知確率は25％です。"
        "- 談合が検知されなかった場合（確率75％）：罰金を支払う必要はありません。"
        "- 談合が検知された場合（確率25％）：罰金250ポイントを支払う必要があります。"

        "提供するチャットログを分析し、以下の情報を抽出してください："
# ... (中略) ...
        "- 談合（共謀・Collusion）の疑いがあるか判断してください（例：事前に勝者を決める、「共謀に誓います」「協力します」といった談合を示唆する発言があるなど）。（ない場合は-1、不明な場合は0、ある場合は1）：Whether_Collusion"
    )

    SystemPROMPT_T6secondfine25 = (
        "経済学実験における参加者間のチャットログを送信します。この実験は、2人（プレイヤー1とプレイヤー2）を1組とした「第二価格オークション（second price auction）」形式で行われます。両参加者は、自分だけが確認できる商品の「評価額（value）」を持っています。"
        "入札前に両者はチャットでコミュニケートすることが可能です。入札後、最も高い価格（bid）を提示した者が勝者となり商品を受け取ります。勝者の利得（payoff）は「評価額 - 2番目に高い入札額（敗者のbid）」となります。また、勝者は自分の利得の一部を敗者に譲渡（transfer）することも選択できます。"

        "【罰金ルール】事前にチャットで交流したり譲渡（transfer）を行ったりした場合、談合（Collusion）とみなされ、両者に250ポイントの罰金が科される可能性があります。今回の談合検知確率は25％です。"
        "- 談合が検知されなかった場合（確率75％）：罰金を支払う必要はありません。"
        "- 談合が検知された場合（確率25％）：罰金250ポイントを支払う必要があります。"

        "提供するチャットログを分析し、以下の情報を抽出してください："
# ... existing code ...

# 读取CSV文件
df = pd.read_csv('logdemo.csv')

all_predictions = []

# 循环处理 ChannelID 1 到 5
for target_channel_id in range(1, 6):
    # 选取特定 ChannelID 的数据
    channel_data = df[df['ChannelID'] == target_channel_id]

    # 构建聊天记录字符串
    chat_lines = []
    for _, row in channel_data.iterrows():
        # 根据 nickname 判断是 player1 还是 player2
        # 假设 nickname 中包含 "1" 即为 player1，否则为 player2
        role = "player1" if "1" in str(row['nickname']) else "player2"
        body = str(row['body'])
        chat_lines.append(f"{role}: {body}")

    print(chat_lines)
    UserPROMPT = "\n".join(chat_lines) #将列表转换为单个字符串，每条聊天记录占一行

    print(f"Processing Channel {target_channel_id}...")

    ##############################################



    response = client.responses.parse(
                model=MODEL,
                input=[
                    {"role": "system",
                     "content": SystemPROMPT},
                    {"role": "user",
                     "content": UserPROMPT}
                ],
                temperature=TEMP,
                text_format=Prediction,
            )

    response_content = response.output_parsed
    
    # 将 Pydantic 对象转换为字典
    prediction_dict = response_content.model_dump()
    # 添加 ChannelID
    prediction_dict['ChannelID'] = target_channel_id
    
    all_predictions.append(prediction_dict)
    print(f"Channel {target_channel_id} prediction collected.")

# 将所有结果转换为 DataFrame 并保存为 CSV
result_df = pd.DataFrame(all_predictions)
# 将 ChannelID 放到第一列
cols = ['ChannelID'] + [col for col in result_df.columns if col != 'ChannelID']
result_df = result_df[cols]

output_filename = 'predictions_output.csv'
result_df.to_csv(output_filename, index=False)
print(f"\nAll predictions saved to {output_filename}")





