import pandas as pd
from os import environ
import time

from openai import OpenAI
from openai import RateLimitError, APIConnectionError, APITimeoutError, APIStatusError
from pydantic import BaseModel, Field

############# Basic Setting ##################

client = OpenAI(
    api_key='himitsu',
    timeout=60.0,
    max_retries=3,
)

MODEL = "gpt-4o"
TEMP = 1
NUM_SAMPLES_PER_OFFER = 100

PRINT_EVERY = 10

OUTPUT_DIR = os.path.join("TestBargaining", "Respond")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class Prediction(BaseModel):
    Whether_to_Accept: bool
    Your_Proposal_if_Reject: int = Field(ge=-1, le=100)

total_groups = 101
total_per_group = NUM_SAMPLES_PER_OFFER
total_steps = total_groups * total_per_group
done = 0

for user_propose in range(101):
    system_prompt = (
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

    user_prompt = (
        "Answer using the schema:\n"
        "- Whether_to_Accept: boolean\n"
        "- Your_Proposal_if_Reject: integer in [-1, 100] (use -1 if accepting)\n"
    )

    # 每个 user_propose 单独收集并单独写文件
    group_predictions = []

    for sample_idx in range(1, NUM_SAMPLES_PER_OFFER + 1):
        done += 1
        if done == 1 or done % PRINT_EVERY == 0 or done == total_steps:
            print(
                f"Progress: group {user_propose + 1}/{total_groups} (user_propose={user_propose}), "
                f"sample {sample_idx}/{total_per_group}, total {done}/{total_steps}",
                flush=True,
            )

        try:
            response = client.responses.parse(
                model=MODEL,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMP,
                text_format=Prediction,
            )
        except RateLimitError as e:
            print(f"[RateLimitError] group={user_propose} sample={sample_idx}: {e}", flush=True)
            time.sleep(5)
            continue
        except (APITimeoutError, APIConnectionError) as e:
            print(f"[Network/Timeout] group={user_propose} sample={sample_idx}: {e}", flush=True)
            time.sleep(2)
            continue
        except APIStatusError as e:
            print(f"[APIStatusError {e.status_code}] group={user_propose} sample={sample_idx}: {e}", flush=True)
            time.sleep(2)
            continue

        prediction = response.output_parsed.model_dump()
        prediction["user_propose"] = user_propose
        prediction["sample_idx"] = sample_idx
        group_predictions.append(prediction)

    group_df = pd.DataFrame(group_predictions)
    front_cols = ["user_propose", "sample_idx"]
    if not group_df.empty:
        group_df = group_df[front_cols + [c for c in group_df.columns if c not in front_cols]]

    output_filename = os.path.join(OUTPUT_DIR, f"Respond_user_propose_{user_propose:03d}.csv")
    group_df.to_csv(output_filename, index=False)
    print(f"Saved: {output_filename} ({len(group_df)} rows)", flush=True)




