import asyncio
import time
import os
import sys
import json
import urllib.request
import urllib.parse

BASE_URL = "https://ai-visibility-platform-production-4b8b.up.railway.app/api/v1"

def req(url, method="GET", data=None):
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    print("=== BACKEND PRODUCTION TEST FOR https://www.myntra.com ===")
    t_start = time.perf_counter()

    # Step 1: Create/Retrieve Project
    t1 = time.perf_counter()
    proj = req(f"{BASE_URL}/projects", method="POST", data={"name": "Myntra", "url": "https://www.myntra.com"})
    proj_id = proj["id"]
    t1_elapsed = (time.perf_counter() - t1) * 1000
    print(f"JOB_CREATED project_id={proj_id} domain={proj['domain']} duration_ms={t1_elapsed:.2f}")

    # Step 2: Create Analysis Job
    t2 = time.perf_counter()
    job = req(f"{BASE_URL}/projects/{proj_id}/jobs", method="POST")
    job_id = job["id"]
    t2_elapsed = (time.perf_counter() - t2) * 1000
    print(f"JOB_STARTED job_id={job_id} initial_status={job['status']} duration_ms={t2_elapsed:.2f}")

    # Step 3: Poll for Completion
    t3 = time.perf_counter()
    completed = False
    for poll_idx in range(1, 40):
        time.sleep(2)
        j_status = req(f"{BASE_URL}/jobs/{job_id}")
        st = j_status["status"]
        t_poll = (time.perf_counter() - t3) * 1000
        print(f"POLL #{poll_idx}: status={st} elapsed_ms={t_poll:.2f}")

        if st == "Completed":
            completed = True
            print(f"GEMINI_COMPLETED job_id={job_id} duration_ms={t_poll:.2f}")
            break
        elif st == "Failed":
            print(f"GEMINI_FAILED job_id={job_id} error={j_status.get('error_message')} duration_ms={t_poll:.2f}")
            break

    if not completed:
        print("JOB_TIMEOUT: Analysis did not complete within 80 seconds.")
        return

    # Step 4: Verify Persisted Result in PostgreSQL
    t4 = time.perf_counter()
    eval_res = req(f"{BASE_URL}/jobs/{job_id}/evaluation")
    t4_elapsed = (time.perf_counter() - t4) * 1000
    print(f"RESULT_SAVED job_id={job_id} domain={eval_res['target_domain']} mentioned={eval_res['mentioned']} evidence_count={len(eval_res.get('evidence_items', []))} duration_ms={t4_elapsed:.2f}")

    total_elapsed = (time.perf_counter() - t_start) * 1000
    print(f"JOB_COMPLETED job_id={job_id} total_duration_ms={total_elapsed:.2f}")
    print("SUCCESS: REAL MYNTRA PRODUCTION ANALYSIS COMPLETED!")

if __name__ == "__main__":
    main()
