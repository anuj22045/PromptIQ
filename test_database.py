
from data.database import test_database_connection

result = test_database_connection()

print("\nDATABASE CONNECTION TEST")
print("Connected:", result["connected"])
print("Database:", result["database"])
print("Error:", result["error"])

assert result["connected"] is True
assert result["database"] == "promptiq_analytics"

print("\nDatabase connection test passed!")
