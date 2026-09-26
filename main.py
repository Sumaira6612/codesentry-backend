import json
from mock_data import MOCK_PR_DIFF
from orchestrator import run_code_sentry_pipeline

if __name__ == "__main__":
    print("🚀 Starting CodeSentry Multi-Agent Pipeline...\n")
    results = run_code_sentry_pipeline(MOCK_PR_DIFF)
    print(json.dumps(results, indent=2))