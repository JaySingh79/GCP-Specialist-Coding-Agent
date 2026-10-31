# import requests
# import json, pathlib
# m=json.loads(pathlib.Path('gcloud_cli_data/_manifest.json').read_text())
# for u in m['failed']:
#     try:
#         r=requests.get(u, headers={"User-Agent":"Mozilla/5.0"}, timeout=20, allow_redirects=True)
#         print(r.status_code, len(r.text), u, "| final:", r.url[:120])
#     except Exception as e:
#         print("ERR", u, e)

import json

with open("gcloud_engineering_agent_benchmark\\gcloud_engineering_agent_benchmark\\gcloud_migration_agent_tasks.jsonl", "r", encoding="utf-8") as f:
    content = list(f)
    
prompts = []
for line in content:
    
    content_line = json.loads(line)
    prompts.append(content_line['task_prompt'])
    
with open('training_prompts.json', "w", encoding="utf-8") as f:
    json.dump(prompts, f)
    
    
