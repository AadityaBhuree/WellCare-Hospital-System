"""Quick verification script for imports, auth, and app initialization."""

print("=" * 50)
print("WellCare App Verification")
print("=" * 50)

# Step 1: Verify imports
print("\n[1/4] Verifying imports...")
from src.wellcare.config import (
    ADMIN_USERNAME, ADMIN_PASSWORD_HASH,
    STAFF_USERNAME, STAFF_PASSWORD_HASH,
    APP_TITLE, DATABASE_PATH,
)
from src.wellcare.utils.auth import authenticate_user
from src.wellcare.utils.validators import validate_mobile, validate_patient_input
from src.wellcare.database import Database
print("  [OK] All imports resolved successfully")
print(f"  APP_TITLE: {APP_TITLE}")
print(f"  DATABASE_PATH: {DATABASE_PATH}")
print(f"  ADMIN_USERNAME: {ADMIN_USERNAME}")
print(f"  ADMIN_PASSWORD_HASH present: {bool(ADMIN_PASSWORD_HASH)}")
print(f"  STAFF_USERNAME: {STAFF_USERNAME}")
print(f"  STAFF_PASSWORD_HASH present: {bool(STAFF_PASSWORD_HASH)}")

# Step 2: Verify bcrypt auth
print("\n[2/4] Verifying bcrypt authentication...")
admin_result = authenticate_user("admin", "123")
staff_result = authenticate_user("staff", "123")
bad_result = authenticate_user("admin", "wrong")
bad_user = authenticate_user("nonexistent", "123")

assert admin_result == "admin", f"Expected 'admin', got {admin_result}"
assert staff_result == "staff", f"Expected 'staff', got {staff_result}"
assert bad_result is None, f"Expected None, got {bad_result}"
assert bad_user is None, f"Expected None, got {bad_user}"
print("  [OK] Admin login (admin/123): admin")
print("  [OK] Staff login (staff/123): staff")
print("  [OK] Wrong password: rejected (None)")
print("  [OK] Unknown user: rejected (None)")

# Step 3: Verify validators
print("\n[3/4] Verifying validators...")
assert validate_mobile("9876543210") is None
assert validate_mobile("123") is not None
assert validate_patient_input("9876543210", "test@test.com", "70", "25") is None
print("  [OK] All validators working correctly")

# Step 4: Verify database initialization
print("\n[4/4] Verifying database initialization...")
db = Database()
assert db.cur is not None, "Database cursor is None - init failed!"
print("  [OK] Database initialized, table 'patients' ready")

print("\n" + "=" * 50)
print("ALL VERIFICATIONS PASSED!")
print("=" * 50)
print("\nApp is ready to launch. Run: python -m src.wellcare")
