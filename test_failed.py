# import requests
# urls=[
# "https://docs.cloud.google.com/sdk/gcloud/reference/beta/auth",
# "https://docs.cloud.google.com/sdk/gcloud/reference/topic/gcloudignore",
# "https://docs.cloud.google.com/sdk/gcloud/reference/storage/hash",
# "https://docs.cloud.google.com/sdk/gcloud/reference/compute/health-checks",
# "https://docs.cloud.google.com/sdk/gcloud/reference/alpha/edge-cache",
# ]
# for u in urls:
#     try:
#         r=requests.get(u, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
#         print(u, r.status_code, len(r.text))
#     except Exception as e:
#         print(u, "ERR", e)


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from functions.tool_batching import batched_tools_function, batched_tools

print(batched_tools.__name__ == "batched_tools")