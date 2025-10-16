import random
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="InfraStory Live Demo (synthetic)")

SCENARIOS = {
    "small":  {"ec2": 2, "rds": 1, "s3": 3, "costs": {"EC2": 28.7, "RDS": 12.5, "S3": 4.2}},
    "medium": {"ec2": 6, "rds": 3, "s3": 7, "costs": {"EC2": 180.3, "RDS": 95.4, "S3": 22.6, "EBS": 18.0}},
    "large":  {"ec2": 18,"rds": 6, "s3": 15,"costs": {"EC2": 920.0, "RDS": 430.0,"S3": 140.0,"EBS": 120.0, "DT": 75.0}}
}
DEFAULT_SAVINGS = {"EC2": 0.20, "RDS": 0.25, "S3": 0.30, "EBS": 0.20, "DT": 0.15}

class LiveResponse(BaseModel):
    ec2_instances: int
    rds_instances: int
    s3_buckets: int
    costs: dict
    recommendations: list
    scenario: str
    note: str = "Synthetic demo – no real cloud access."

def build_recs(costs: dict):
    recs = []
    for svc, cost in costs.items():
        pct = DEFAULT_SAVINGS.get(svc, 0.0)
        if pct > 0 and cost > 0:
            recs.append(f"{svc}: potential savings ~ {cost*pct:.2f} $ (~{int(pct*100)}%).")
    if "DT" in costs and costs["DT"] > 0:
        recs.append("Data Transfer: use CloudFront, VPC endpoints; reduce cross-AZ/region traffic.")
    if costs.get("S3", 0) > 0:
        recs.append("S3: lifecycle to IA/Glacier, compress small objects.")
    if costs.get("EC2", 0) > 0:
        recs.append("EC2: rightsizing & modern families; stop non-prod off-hours.")
    return recs

@app.get("/inventory", response_model=LiveResponse)
def inventory(scenario: str = "small"):
    scenario = scenario if scenario in SCENARIOS else "small"
    s = SCENARIOS[scenario].copy()
    jitter = lambda x: max(0, round(x * random.uniform(0.97, 1.06), 2))
    costs = {k: jitter(v) for k, v in s["costs"].items()}
    recs = build_recs(costs)
    return LiveResponse(
        ec2_instances=s["ec2"],
        rds_instances=s["rds"],
        s3_buckets=s["s3"],
        costs=costs,
        recommendations=recs,
        scenario=scenario,
    )
