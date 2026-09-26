import concurrent.futures
import time
from agents.security_agent import analyze_security
from agents.test_agent import generate_tests
from agents.breaking_agent import detect_breaking_changes
from agents.changelog_agent import draft_changelog

def run_code_sentry_pipeline(pr_diff: str) -> dict:
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f_sec = executor.submit(analyze_security, pr_diff)
        f_test = executor.submit(generate_tests, pr_diff)
        f_break = executor.submit(detect_breaking_changes, pr_diff)
        f_change = executor.submit(draft_changelog, pr_diff)

        security_data = f_sec.result()
        missing_tests = f_test.result()
        breaking_changes = f_break.result()
        changelog = f_change.result()

    execution_time = round(time.time() - start_time, 2)

    return {
        "status": "SUCCESS",
        "execution_time_seconds": execution_time,
        "pull_request_id": "PR-104",
        "security_score": security_data["score"],
        "merge_readiness": "NEEDS_FIXES" if security_data["score"] < 80 else "READY",
        "security_issues": security_data["issues"],
        "generated_tests": missing_tests,
        "breaking_changes": breaking_changes,
        "draft_changelog": changelog
    }