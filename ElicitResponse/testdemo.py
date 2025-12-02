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

SystemPROMPT = (
    "我将发送给你一个经济学实验中的参与者之间的聊天记录；该经济学实验是一个两个人（player1 和player2）为一组的first price auction实验。 两个参与者都有各自的，只能自己看到的，对于拍卖的商品的value（評価額）,"
    "在双方入札之前，双方可以选择进行进行chat交流；入札之后，bid价高者胜，获得商品，其收益为:評価額-出价bid；同时，胜者也可以选择将收益（payoff）中的一部分（transfer）分给败者"
    "现在，请帮我分析聊天记录，并提取一些关键信息:"
    "-player1是否告知自己的評価額（一个数字）：player1_whether_inform_exact_self_value"
    "-player2是否告知自己的評価額（一个数字）：player2_whether_inform_exact_self_value"
    "-player1是否告知自己的評価額的区间：player1_whether_inform_value_interval"
    "-player2是否告知自己的評価額的区间：player2_whether_inform_value_interval"
    "-如果player1有告知自己的評価額，那么这个評価額是多少 (如果没有的话则返回-1)：player1_inform_exact_self_value"
    "-如果player2有告知自己的評価額，那么这个評価額是多少 (如果没有的话则返回-1)：player2_inform_exact_self_value"
    "-如果player1有告知自己的評価額的区间，那么这个区间是多少(如果没有的话则返回-1)：player1_inform_value_interval_minbound, player1_inform_value_interval_maxbound"
    "-如果player2有告知自己的評価額的区间，那么这个区间是多少(如果没有的话则返回-1)：player2_inform_value_interval_minbound, player2_inform_value_interval_maxbound"
    "-player1是否告诉对方自己的之后的bid(一个数字)：player1_whether_inform_exact_self_bid"
    "-player2是否告诉对方自己的之后的bid(一个数字)：player2_whether_inform_exact_self_bid"
    "-player1是否告诉对方自己的之后的bid区间：player1_whether_inform_bid_interval"
    "-player2是否告诉对方自己的之后的bid区间：player2_whether_inform_bid_interval"
    "-如果player1有告诉对方自己的之后的bid，那么这个bid是多少(如果没有的话则返回-1)：player1_inform_exact_self_bid"
    "-如果player2有告诉对方自己的之后的bid，那么这个bid是多少(如果没有的话则返回-1)：player2_inform_exact_self_bid"
    "-注意：这里的bid是出价，而不是payoff（利得）"
    "-如果player1有告诉对方自己的之后的bid区间，那么这个区间是多少(如果没有的话则返回-1)：player1_inform_bid_interval_minbound, player1_inform_bid_interval_maxbound"
    "-如果player2有告诉对方自己的之后的bid区间，那么这个区间是多少(如果没有的话则返回-1)：player2_inform_bid_interval_minbound, player2_inform_bid_interval_maxbound"
    "-双方是否提前决定winner(如果没有提前决定返回-1，如果决定是either one则返回0，如果决定是player1则返回1，如果决定是player2则返回2)：Whether_Pre_Decide_Winner"
    "-当双方提前决定winner的时候，判断约定胜者给败者transfer的format, 返回following的五个选项之一，'50% of the payoff'/ 'Exact number' /'Interval'/'Some points (not specific)'/'Nothing(not mentioned or no pre-decided winner)': Pre_Decide_Winner_Committed_Transfer_Format"
    "-胜者约定的给败者transfer的具体金额数字是多少(如果没有返回-1)：Pre_Decide_Winner_Committed_Transfer_Number"
    "-胜者约定的给败者transfer的具体金额数字的区间是多少(如果没有返回-1)：Pre_Decide_Winner_Committed_Transfer_interval_minbound, Pre_Decide_Winner_Committed_Transfer_interval_maxbound"
    "-判断是否双方有勾结(比如双方有提前决定winner，或者使用一些「共謀に誓います」、「協力します」等等可以表示双方有在勾结Collusion的象征或者象征)(如果没有返回-1，如果不确定则返回0，如果有勾结则返回1)：Whether_Collusion"
)

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





