#!/usr/bin/env python3
"""The smallest useful thing: measure one LLM call from a LangChain chain.

Run it for free first -- `submit=False` opens no socket:

    python examples/01_minimal.py --dry-run

Then, with a real key, measure for real (0.030 CHF per observation):

    export NEOMUNDI_API_KEY=ct_live_...
    python examples/01_minimal.py
"""

from __future__ import annotations

import argparse
import os
import sys

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from langchain_neomundi import NeoMundiCallbackHandler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="measure locally, submit nothing")
    parser.add_argument("--base-url", default="https://api.neomundi.io")
    parser.add_argument("--model", default="llama3.2:3b")
    args = parser.parse_args()

    api_key = os.environ.get("NEOMUNDI_API_KEY")
    if not api_key:
        print("Set NEOMUNDI_API_KEY. The base URL is never assumed.", file=sys.stderr)
        return 2

    handler = NeoMundiCallbackHandler(
        api_key=api_key,
        base_url=args.base_url,
        submit=not args.dry_run,
    )

    chain = ChatPromptTemplate.from_messages([("human", "{question}")]) | ChatOllama(
        model=args.model, temperature=0
    )

    answer = chain.invoke(
        {"question": "In one sentence, what is the capital of France?"},
        config={"callbacks": [handler]},
    )

    print(f"answer   : {answer.content.strip()}")

    outcome = handler.last_outcome
    print(f"status   : {outcome.status}")
    print(f"submitted: {outcome.submitted}")
    print(f"latency  : {outcome.latency_ms:.0f} ms (measured, not declared)")
    print(f"tokens   : {outcome.token_count}")
    print(f"requestid: {outcome.request_id}")

    if not outcome.submitted:
        # Never a silent gap: the handler always says why.
        print(f"reason   : {outcome.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
