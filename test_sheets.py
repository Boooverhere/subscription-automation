from services.sheets_service import get_sheet, get_all_subscribers

# Connect to the sheet
worksheet = get_sheet()

# Read all subscribers
subscribers = get_all_subscribers(worksheet)

# Print each subscriber
for i, subscriber in enumerate(subscribers):
    print(f"\n--- Subscriber {i + 1} ---")
    for key, value in subscriber.items():
        print(f"  {key}: {value}")
