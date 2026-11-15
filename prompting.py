from openpyxl import load_workbook
import yaml
from prompt_engineering.scoring import check, extract_json
wb = load_workbook(r"C:\Projects\promptengg\TestData.xlsx", read_only=True, data_only=True)
ws = wb.active                       # or wb["Sheet1"]

rows = ws.iter_rows(values_only=True)
header = next(rows)
data = [dict(zip(header, r)) for r in rows]



from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Required by the client library; Ollama ignores it locally
)

with open("prompts.yaml", 'r') as file:
    prompts = yaml.safe_load(file)
    #system_prompt = "Extract the important information from this email."
    system_prompt = prompts.get("version1")
    system_prompt=system_prompt +prompts.get("version2")

    print("System Prompt: ", system_prompt) 
# loop this for each email in the data list
passed=0
for email in data:
    print("\n Email: ", email["Email"])
    response = client.chat.completions.create(model="gemma4:e2b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": email["Email"]},
        ],
        temperature=0,
        reasoning_effort="none",  # "none" = thinking off | "low" / "medium" / "high" = thinking on
        )
    content=response.choices[0].message
    print(response.choices[0].message.content)
    parsed = extract_json(content)     # None if the reply isn't pure JSON
    problems = check(parsed, email)
    if problems:
        print("\n\nFAIL:", "; ".join(problems))
    else:
        print("PASS")
        passed += 1

#print(f"\nScore: {passed}/{len(data)}")

