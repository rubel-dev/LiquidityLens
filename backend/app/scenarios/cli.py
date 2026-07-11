import argparse
import sys
from datetime import datetime
from typing import cast

from app.persistence.database import SessionLocal
from app.scenarios.exceptions import ScenarioError
from app.scenarios.schemas import ProfileName, ScenarioConfig, ScenarioRunResult
from app.scenarios.service import ScenarioService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.scenarios.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("scenario_code")
    run_parser.add_argument("--seed", default="1001")
    run_parser.add_argument("--profile", choices=["small", "medium", "demo"], default="small")
    run_parser.add_argument("--start-timestamp")
    run_parser.add_argument("--run-id")

    reset_parser = subparsers.add_parser("reset")
    reset_parser.add_argument("--run-id", required=True)

    replay_parser = subparsers.add_parser("replay")
    replay_parser.add_argument("--run-id", required=True)

    args = parser.parse_args(argv)
    try:
        with SessionLocal() as session:
            service = ScenarioService(session)
            if args.command == "list":
                for scenario in service.list_scenarios():
                    print(f"{scenario['code']}: {scenario['name']}")
                return 0
            if args.command == "run":
                start_timestamp = (
                    datetime.fromisoformat(args.start_timestamp) if args.start_timestamp else None
                )
                result = service.run_scenario(
                    args.scenario_code,
                    args.seed,
                    ScenarioConfig(
                        profile=cast(ProfileName, args.profile),
                        start_timestamp=start_timestamp,
                        requested_run_ref=args.run_id,
                    ),
                )
                _print_result(result)
                return 0
            if args.command == "reset":
                result = service.reset(args.run_id)
                _print_result(result)
                return 0
            if args.command == "replay":
                result = service.replay(args.run_id)
                _print_result(result)
                return 0
    except (ScenarioError, ValueError) as exc:
        print(f"scenario command failed: {exc}", file=sys.stderr)
        return 1
    return 1


def _print_result(result: ScenarioRunResult) -> None:
    print(f"run_ref={result.run_ref}")
    print(f"scenario={result.scenario_code}")
    print(f"status={result.status}")
    print(f"seed={result.seed}")
    if result.fingerprint:
        print(f"fingerprint={result.fingerprint}")
    if result.generated_counts:
        print(f"counts={result.generated_counts}")


if __name__ == "__main__":
    raise SystemExit(main())
