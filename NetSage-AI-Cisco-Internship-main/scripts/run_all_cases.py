import os
import json
import csv
import urllib.request
import urllib.error
import time

API_KEY = os.environ.get("GEMINI_API_KEY")

def call_gemini(prompt_text):
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None

def build_prompt(row):
    return f"""
Analyze the following network incident and determine the root cause, OSI layer, confidence level, supporting CLI evidence, next diagnostic command, and step-by-step Cisco IOS remediation steps. 
Respond STRICTLY with a valid JSON object matching this exact schema:
{{
  "root_cause": "<Precise description of the fault>",
  "osi_layer": "<Data Link (Layer 2) | Network (Layer 3) | Transport (Layer 4) | Application (Layer 7)>",
  "concept_tag": "{row['concept_tag']}",
  "confidence": "<High | Medium | Low>",
  "evidence": ["<Primary CLI output line citation>"],
  "next_command": "<Cisco IOS verification command>",
  "fix_steps": ["<remediation command 1>", "<remediation command 2>"]
}}

### 1. Incident Symptom
{row['symptom']}

### 2. Topology Context & Host Notes
{row['topology_note']}

### 3. Captured Cisco IOS Show Commands
{row['show_output_evidence']}
"""

def main():
    print("NetSage AI - Batch Execution Script")
    print("-----------------------------------")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "cases.csv")
    output_dir = os.path.join(base_dir, "data", "llm_outputs")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            case_id = row['case_id']
            output_file = os.path.join(output_dir, f"{case_id}_output.json")
            
            if os.path.exists(output_file):
                print(f"Skipping {case_id}, output already exists.")
                continue
                
            print(f"Sending {case_id} to Gemini API...")
            prompt = build_prompt(row)
            
            try:
                response_json = call_gemini(prompt)
                if response_json:
                    with open(output_file, "w") as out_f:
                        out_f.write(response_json)
                    print(f"Saved {output_file}")
            except Exception as e:
                print(f"Error processing {case_id}: {e}")
                
            print("Sleeping for 15 seconds to respect free-tier rate limits (5 RPM)...")
            time.sleep(15)

if __name__ == "__main__":
    main()
