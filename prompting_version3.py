from typing import Literal, Optional
from prompt_engineering.scoring import check, extract_json
import yaml
from openai import OpenAI
from openpyxl import load_workbook
from pydantic import BaseModel, ValidationError


# ---------- Step 3: the schema ----------
class Ticket(BaseModel):
    order_id: Optional[str]
    category: Literal["damaged_item", "delivery_issue", "billing_issue",
                      "missing_item", "return_request", "pre_sales_question", "other"]
    urgency: Literal["low", "medium", "high"]
    customer_sentiment: Literal["positive", "neutral", "negative", "angry"]
    requested_action: str


USE_SCHEMA = True   # flip to False to show the before/after on camera

# ---------- Data ----------
wb = load_workbook(r"C:\Projects\promptengg\TestData.xlsx", read_only=True, data_only=True)
ws = wb.active
rows = ws.iter_rows(values_only=True)
header = next(rows)
data = [dict(zip(header, r)) for r in rows if r[0]]

# ---------- Prompt ----------
with open("prompts.yaml", "r") as file:
    prompts = yaml.safe_load(file)
system_prompt = prompts.get("version1") + prompts.get("version2")

# ---------- Model ----------
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "gemma4:e2b"
passed = 0
for email in data:
    print("\nEmail:", email["Email"])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": email["Email"]},
    ]

    if USE_SCHEMA:
        try:
            completion = client.chat.completions.parse(
                model=MODEL,
                messages=messages,
                response_format=Ticket,   # the schema is enforced during generation
                temperature=0,
                reasoning_effort="none",  # "none" = thinking off | "low" / "medium" / "high" = thinking on
            
            )
            ticket = completion.choices[0].message.parsed   # a Ticket object
            print(ticket.model_dump_json(indent=2))
        except ValidationError as e:
            print("Schema validation failed:", e)
    else:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0,
            reasoning_effort="none",  # "none" = thinking off | "low" / "medium" / "high" = thinking on
        )
        print(response.choices[0].message.content)
  
    parsed = ticket.model_dump() if ticket else None   # Ticket -> dict
    problems = check(parsed, email)    # None if the reply isn't pure JSON
    
    if problems:
            print("\n\nFAIL:", "; ".join(problems))
    else:
            print("PASS")
            passed += 1
    
#print(f"\nScore: {passed}/{len(data)}")
    