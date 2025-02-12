
def on_age_change(value: any, contest: dict) -> str:
    print(f"on_age_change {value}")
    print(contest)
    for k, val in contest.items():
         print(k, val)
    return "cioo"