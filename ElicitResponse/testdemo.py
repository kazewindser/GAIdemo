import pandas as pd
from os import environ
from openai import OpenAI
from pydantic import BaseModel

############# Basic Setting ##################

client = OpenAI(api_key=environ.get('OPENAI_API_KEY'))

MODEL = "gpt-4o"
TEMP = 1

class Prediction(BaseModel):
    player1_whether_inform_exact_value: bool
    player2_whether_inform_exact_value: bool
    player1_whether_inform_value_interval: bool
    player2_whether_inform_value_interval: bool
    player1_whether_inform_value_interval_minbound: float
    player1_whether_inform_value_interval_maxbound: float
    player2_whether_inform_value_interval_minbound: float
    player2_whether_inform_value_interval_maxbound: float
##############################################

############# PROMPT ##################
SystemPROMPT = (
    ""
)

UserPROMPT = ""
##############################################



 completion = client.responses.parse(
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

response_content = completion.output_parsed
print("prediction: ", response_content)

prediction = completion.output_parsed  # 类型：Prediction
mean = prediction.mean
print("\nmean: ", mean)

record = prediction.model_dump()  # 用model_dump() 方法将class转换成dict
record["prediction_round"] = pred_num  # 加一个额外字段
all_results.append(record)



