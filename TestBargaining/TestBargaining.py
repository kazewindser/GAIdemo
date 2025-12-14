import pandas as pd
from os import environ

from openai import OpenAI
from pydantic import BaseModel, Field

############# Basic Setting ##################

client = OpenAI(api_key=environ.get('AI_Bargaining_KEY'))

MODEL = "gpt-4o"
TEMP = 1


class Prediction(BaseModel):
    Your_Proposal: int=Field(ge=0, le=100)




##############################################

############# PROMPT ##################

SystemPROMPT = (
    "You are a strategic bargaining game AI. Respond only with a number."
    "You are the proposer in a 3-stage alternating-offers bargaining game over 100 points."
    "Your goal: Maximize your own discounted payoff. Your opponent is human。"
    
    "- Total points to divide: 100"
    "- Your role: Proposal"
    "- Current stage: 1 out of 3"
    "- Your discount rate at this stage: 0"
    "- Opponent's discount rate: 0"
    

    "Rules:"
               
    "- You propose how many points to give to your opponent (0-100)"
    "- You keep the remaining points"
    "- If the offer is rejected by your opponent, the game moves to the next stage with higher discounts"
    "- 同时双发角色互换，你成为responder，用户成为proposer"
)

UserPROMPT = ("Based on current situation, what points would you offer to your opponent?"
    "Please respond with ONLY a integer between 0 and 100: Your_Proposal"
              )


all_predictions = []

# 循环处理 ChannelID 1 到 5
for i in range(1, 4):
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

    all_predictions.append(prediction_dict)


# 将所有结果转换为 DataFrame 并保存为 CSV
result_df = pd.DataFrame(all_predictions)


output_filename = 'Proposal.csv'
result_df.to_csv(output_filename, index=False)
print(f"\nAll predictions saved to {output_filename}")





