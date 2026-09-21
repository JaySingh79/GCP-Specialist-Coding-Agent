import subprocess
import json

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()

project = "claude-code-498910"
print(f"=== Project: {project} ===\n")

print("--- VPC Networks & Subnets ---")
networks = run_cmd(f"gcloud compute networks list --project={project} --format=json")
print(json.dumps(networks, indent=2))

print("\n--- Firewall Rules ---")
firewalls = run_cmd(f"gcloud compute firewall-rules list --project={project} --format=json")
print(json.dumps(firewalls, indent=2))

print("\n--- Routes ---")
routes = run_cmd(f"gcloud compute routes list --project={project} --format=json")
print(json.dumps(routes, indent=2))

print("\n--- NAT Configurations (Cloud Routers) ---")
routers = run_cmd(f"gcloud compute routers list --project={project} --format=json")
if isinstance(routers, list):
    for r in routers:
        name = r.get("name")
        region = r.get("region", "").split("/")[-1]
        print(f"\nRouter: {name} (Region: {region})")
        nats = run_cmd(f"gcloud compute routers nats list --router={name} --region={region} --project={project} --format=json")
        print(json.dumps(nats, indent=2))
else:
    print(routers)
