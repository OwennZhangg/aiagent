import re

from agents.planning import planning_agent
from agents.production import (
    production_agent,
    save_script_for_review,
    wait_for_script_approval,
)
from agents.image import image_agent

from config import OUTPUT_DIR

def _topic_slug(topic: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        topic.lower(),
    ).strip("-")

    return slug or "video"

def main() -> None:
    topic = input("What video are you making today? ").strip()

    if not topic:
        print("Error: topic can't be empty.")
        return

    print("Planning video...")

    try:
        plan = planning_agent(topic)
    except Exception as error:
        print(f"Could not create video plan: {error}")
        return
    
    print("✓ Video plan created")
    print("Writing production script...")

    try:
        production = production_agent(plan)
    except Exception as error:
        print(
            f"Could not create production script: {error}"
        )
        return

    # Save the plan and script to disk for review and editing
    run_directory = OUTPUT_DIR / _topic_slug(topic)

    run_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    plan_path = run_directory / "plan.json"

    plan_path.write_text(
        plan.model_dump_json(indent=2),
        encoding="utf-8",
    )

    script_path = save_script_for_review(
        production,
        run_directory / "script.md",
    )

    print(f"✓ Script ready: {script_path}")

    # Wait for the user to approve the script before proceeding
    try:
        approved_production = wait_for_script_approval(
            production,
            script_path,
        )
    except Exception as error:
        print(
            f"Could not approve production script: {error}"
        )
        return
    
    # Save the approved production plan to disk
    production_path = run_directory / "production.json"

    production_path.write_text(
        approved_production.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print("✓ Script approved")
    print(f"✓ Approved production plan: {production_path}")
    print("Finding supporting images...")

    selected_images = image_agent(
        approved_production,
        run_directory,
    )

    successful_images = sum(
        path is not None
        for path in selected_images.values()
    )

    print(
        f"✓ Image work complete: "
        f"{successful_images} images selected"
    )

if __name__ == "__main__":
    main()
