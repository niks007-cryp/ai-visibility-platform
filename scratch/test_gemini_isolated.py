import asyncio
import time
import os
import sys

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.providers.gemini import GeminiProvider
from app.core.config import settings

async def main():
    print("=== ISOLATED GEMINI DIAGNOSTIC TEST ===")
    
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not configured in environment or settings!")
        return

    provider = GeminiProvider(api_key=api_key, model_name="gemini-2.5-flash")
    
    start_time = time.perf_counter()
    try:
        output = await provider.query(
            prompt="Return exactly: GEMINI_25_FLASH_TEST_OK",
            domain="diagnostic-test.com"
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        print(f"MODEL USED: {provider.model_name}")
        print(f"RESPONSE: {output.raw_response.strip()}")
        print(f"DURATION: {elapsed_ms:.2f} ms")
        print("SUCCESS: GEMINI 2.5 FLASH ISOLATED TEST PASSED!")
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"MODEL USED: {provider.model_name}")
        print(f"ERROR: {exc}")
        print(f"DURATION: {elapsed_ms:.2f} ms")
        print("FAILURE: GEMINI 2.5 FLASH ISOLATED TEST FAILED!")

if __name__ == "__main__":
    asyncio.run(main())
