import fastf1

fastf1.Cache.enable_cache("./ff1_cache")

session = fastf1.get_session(2025, "Silverstone", "R")
session.load()

print(f"Race: {session.event['EventName']}")
print(f"Session: {session.name}")
print(f"Date: {session.date}")
print(f"Drivers: {len(session.drivers)}")
print("Top 3:")
for i, row in session.results.head(3).iterrows():
    print(f"  {row['Position']:.0f}. {row['FullName']} ({row['TeamName']})")
