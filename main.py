from agents.planning import planning_agent


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

    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
