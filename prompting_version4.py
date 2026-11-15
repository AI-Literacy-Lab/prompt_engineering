from typing import Literal, Optional
from prompt_engineering.scoring import check, extract_json
import yaml
from openai import OpenAI
from openpyxl import load_workbook
from pydantic import BaseModel, ValidationError

class Ticket(BaseModel):
    order_id: Optional[str]
    category: Literal["damaged_item", "delivery_issue", "billing_issue",
                      "missing_item", "return_request", "pre_sales_question", "other"]
    urgency: Literal["low", "medium", "high"]
    customer_sentiment: Literal["positive", "neutral", "negative", "angry"]
    requested_action: str


USE_SCHEMA = True
   # "none" = thinking off | "low" / "medium" / "high" = thinking on

# ---------- Data ----------
wb = load_workbook(r"C:\Projects\promptengg\TestData.xlsx", read_only=True, data_only=True)
ws = wb.active
rows = ws.iter_rows(values_only=True)
header = next(rows)
data = [dict(zip(header, r)) for r in rows]

# ---------- Prompt ----------
thinking_prompt ="\n\nThink step by step first, then give the final JSON on the last line."
THINKING = "medium" 

with open("prompts.yaml", "r") as file:
    prompts = yaml.safe_load(file)
system_prompt = prompts.get("version1") + prompts.get("version2")+ (thinking_prompt if THINKING != "none" else "")  
# ---------- Model ----------
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "gemma4:e2b"

print(f"Model: {MODEL} | thinking: {THINKING} | schema: {USE_SCHEMA}")
passed=0
for email in data:
    print("\nEmail:", email["Email"])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": email["Email"]},
    ]
    THINKING = "medium" 

    if USE_SCHEMA:
        try:
            completion = client.beta.chat.completions.parse(
                model=MODEL,
                messages=messages,
                response_format=Ticket,
                temperature=0,
                reasoning_effort=THINKING,     # <-- the thinking switch
            )
            msg = completion.choices[0].message
            print(msg.parsed.model_dump_json(indent=2) if msg.parsed else msg.content)
            parsed = msg.parsed.model_dump() if msg.parsed else None
        except ValidationError as e:
            print("Schema validation failed:", e)
            continue
    else:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            reasoning_effort=THINKING,         # <-- the thinking switch
        )
        msg = completion.choices[0].message
        print(msg.content)
        parsed = extract_json(msg.content)

    problems = check(parsed, email)    # None if the reply isn't pure JSON
        
    if problems:
                print("\n\nFAIL:", "; ".join(problems))
    else:
                print("PASS")
                passed += 1
        
        
    #Thinking text (empty when thinking is off) and cost
    print("Thinking:", getattr(msg, "reasoning", None) or "(none)")
    print("Output tokens:", completion.usage.completion_tokens)
#print(f"\nScore: {passed}/{len(data)}")