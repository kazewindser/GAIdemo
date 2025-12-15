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
    "You are a strategic bargaining game AI.\n"
    "Return output in a structured format that matches the given schema.\n"
    "You are the proposer in a 3-stage alternating-offers bargaining game over 100 points.\n"
    "Goal: maximize your own discounted payoff.\n"
    "\n"
    "Current situation:\n"
    "- Total points to divide: 100\n"
    "- Your role: Proposer\n"
    "- Current stage: 1 out of 3\n"
    "- Your discount rate at this stage: 0\n"
    "- Opponent's discount rate: 0\n"
    "\n"
    "Rules:\n"
    "- You propose how many points to give to your opponent (0-100)\n"
    "- You keep the remaining points\n"
    "\n"
    "- If rejected, the game moves to the next stage with higher discounts and roles switch\n"
    "- Your role will change to Responder\n"
    "- Your discount rate will change to 0.4\n"
    "- Opponent's discount rate will change to 0.6\n"
)

UserPROMPT = (
    "Answer using the schema:\n"
    "- Your_Proposal: integer in [0, 100] (points you give to the opponent)\n"
)

all_predictions = []

for round_idx in range(1, 1001):
    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": SystemPROMPT},
            {"role": "user", "content": UserPROMPT},
        ],
        temperature=TEMP,
        text_format=Prediction,
    )

    prediction = response.output_parsed
    all_predictions.append(prediction.model_dump())

result_df = pd.DataFrame(all_predictions)

output_filename = "Proposal.csv"
result_df.to_csv(output_filename, index=False)
print(f"\nAll predictions saved to {output_filename}")





