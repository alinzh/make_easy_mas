import json
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from mas_lib.connectors.llm_connectors import get_llm_client

load_dotenv(".env")
MODEL = "meta-llama/llama-4-maverick"
llm = get_llm_client(model=MODEL, temperature=0.0)

class TraceEval(BaseModel):
    correct: bool = Field(description="True if final answer appears logically correct")
    confidence: float = Field(ge=0, le=1, description="Confidence in judgment (0-1)")
    issues: list[str] = Field(description="Specific problems detected")
    explanation: str = Field(description="Step-by-step reasoning")

structured_llm = llm.with_structured_output(TraceEval)

def validate_trace(obs):    
    msg = f"""ANALYZE THIS AGENT TRACE AND JUDGE FINAL ANSWER VALIDITY:

EVALUATION CRITERIA (analyze trace only):
1. LOGICAL CORRECTNESS - Does final answer match initial task?
2. ERROR IMPACT - how many errors found? Critical vs minor?
3. COMPLEXITY - Excessively long/complex for simple task? 
4. CONSISTENCY - Reasoning aligns with observations?
5. COMPLETENESS - Task fully resolved?

TRACE ({len(obs)} steps):
{obs}

DETAILED ANALYSIS REQUIRED:
1. What was the task? (infer from first observation)
2. What is final answer? (last observation)  
3. Are they logically consistent?
4. Did errors block success?
5. Signs of hallucination/confusion?

JUDGMENT:
- correct: True/False (final answer solves task)
- confidence: 0.0-1.0 (your certainty)
- issues: specific problems found
- explanation: your reasoning process"""

    return structured_llm.invoke([msg])

results = []
for f in Path("examples/traces").glob("*.json"):
    data = json.loads(f.read_text())
    obs = data.get("trace", {}).get("observations", [])
    
    if obs:
        eval_result = validate_trace(obs)
        results.append({"file": f.name, "eval": eval_result.dict()})
        print(f"{f.name}: {'CORRECT' if eval_result.correct else 'WRONG'} (conf: {eval_result.confidence:.2f})")

json.dump(results, open("validation.json", "w"), indent=2)
correct_count = sum(r['eval']['correct'] for r in results)
print(f"\n{correct_count}/{len(results)} correct ({correct_count/len(results)*100:.1f}%)")
