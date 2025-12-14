import pandas as pd
from os import environ

from openai import OpenAI
from pydantic import BaseModel, Field

############# Basic Setting ##################

client = OpenAI(api_key=environ.get('AI_Bargaining_KEY'))

MODEL = "gpt-4o"
TEMP = 1


class Prediction(BaseModel):
    Whether_to_Accept: bool
    Your_Proposal_if_Reject: int = Field(ge=-1, le=100)


##############################################

############# PROMPT ##################
user_propose = 0

SystemPROMPT = (
    "You are a strategic bargaining game AI.\n"
    "Return output in a structured format that matches the given schema.\n"
    "Game: a 3-stage alternating-offers bargaining game over 100 total points.\n"
    "Goal: maximize your own discounted payoff.\n"
    "\n"
    "Current situation:\n"
    "- Total points to divide: 100\n"
    "- Your role: Responder\n"
    "- Current stage: 1 out of 3\n"
    "- Your discount rate at this stage: 0\n"
    "- Opponent's discount rate: 0\n"
    f"- Points you would receive if you accept now (before discount): {user_propose}\n"
    "\n"
    "If you reject, the game moves to stage 2 out of 3:\n"
    "- Your role will change to Proposer\n"
    "- Your discount rate will change to 0.6\n"
    "- Opponent's discount rate will change to 0.4\n"
    "\n"
    "Decide whether to accept. If rejecting, propose an integer offer (0-100) "
    "representing how many points you would give the opponent next stage.\n"
)

UserPROMPT = (
    "Answer using the schema:\n"
    "- Whether_to_Accept: boolean\n"
    "- Your_Proposal_if_Reject: integer in [-1, 100] (use -1 if accepting)\n"
)

all_predictions = []

for round_idx in range(1, 4):
    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": SystemPROMPT + f"\nRound: {round_idx}\n"},
            {"role": "user", "content": UserPROMPT},
        ],
        temperature=TEMP,
        text_format=Prediction,
    )

    prediction = response.output_parsed
    all_predictions.append(prediction.model_dump())

result_df = pd.DataFrame(all_predictions)

output_filename = "Respond.csv"
result_df.to_csv(output_filename, index=False)
print(f"\nAll predictions saved to {output_filename}")




