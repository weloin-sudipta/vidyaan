# Vidyaan Setup Process

## Overview

Vidyaan provides a comprehensive setup process to initialize a new institute with:
- **Institute (Company)** - Main organization entity
- **Institute Admin User** - Administrator with full permissions and password
- **System Configuration** - Default settings and global defaults
- **Role-Based Access** - Integrated with Frappe's permission system

## Architecture

The setup system is organized in stages, similar to ERPNext's setup wizard:

```
vidyaan/setup/
├── setup_stages.py          # Main orchestrator with 5 stages
├── operations/
│   ├── install_fixtures.py  # Install default data
│   └── institute_setup.py   # Create institute & admin user
├── setup_wizard.py          # Frappe whitelist endpoints
├── wizard.py                # Legacy functions + new integration
└── test_setup.py            # Test utilities
```

## Setup Stages

### Stage 1: Install Presets
- Creates Address Template for country
- Ensures Country record exists
- Ensures Currency (INR) exists
- Enables currency for use

### Stage 2: Setup Institute
- Creates Company with education configuration
- Auto-generates unique abbreviation
- Sets default currency and country
- Configures chart of accounts

### Stage 3: Create Institute Admin User
- Creates User with Institute Admin and System Manager roles
- Sets password securely using Frappe's password utility
- Ensures roles exist before assigning
- Sets user type to "System User"

### Stage 4: Setup Defaults
- Configures Global Defaults
- Sets default company
- Sets default currency
- Sets country

### Stage 5: Finalization
- Marks setup as complete
- Updates installed application flags
- Commits all transactions

## Usage

### Via Python CLI

```python
from vidyaan.setup.setup_stages import setup_complete

args = frappe._dict({
    'institute_name': 'My Institute',
    'institute_abbr': 'MI',
    'admin_email': 'admin@example.com',
    'admin_name': 'Administrator',
    'admin_password': 'SecurePassword123',
    'country': 'India',
    'currency': 'INR'
})

setup_complete(args)
```

### Via Bench Command

```bash
benchmark --site yoursitename execute vidyaan.setup.setup_stages.setup_complete
```

### Via API (Frontend/HTTP)

```javascript
frappe.call({
    method: 'vidyaan.setup.setup_wizard.run_setup',
    args: {
        setup_data: JSON.stringify({
            institute_name: 'My Institute',
            institute_abbr: 'MI',
            admin_email: 'admin@example.com',
            admin_name: 'Administrator',
            admin_password: 'SecurePassword123',
            country: 'India',
            currency: 'INR'
        })
    },
    callback: function(r) {
        if (r.message.success) {
            frappe.msgprint('Setup completed successfully!');
            // Redirect to desk
            frappe.boot.setup_complete = 1;
            window.location.href = '/app/home';
        } else {
            frappe.msgprint('Error: ' + r.message.message);
        }
    }
});
```

### Legacy Mode (Backward Compatible)

```python
from vidyaan.setup.wizard import complete_setup

# Just institute name - creates company only
complete_setup('My Institute')

# Full mode - creates company and admin user
complete_setup('My Institute', 'admin@example.com', 'password123')
```

## API Endpoints

### 1. Get Setup Data
**Method:** `vidyaan.setup.setup_wizard.get_setup_data`

**Returns:**
```json
{
    "setup_complete": false,
    "countries": ["India", "USA", ...],
    "currencies": ["INR", "USD", ...]
}
```

### 2. Run Setup
**Method:** `vidyaan.setup.setup_wizard.run_setup`

**Parameters:**
```json
{
    "setup_data": "{...JSON setup parameters...}"
}
```

**Returns:**
```json
{
    "success": true,
    "message": "Setup completed successfully",
    "admin_email": "admin@example.com",
    "institute_name": "My Institute"
}
```

### 3. Validate Institute Name
**Method:** `vidyaan.setup.setup_wizard.validate_institute_name`

**Parameters:**
```json
{
    "institute_name": "My Institute"
}
```

**Returns:**
```json
{
    "valid": true,
    "message": ""
}
```

### 4. Validate Admin Email
**Method:** `vidyaan.setup.setup_wizard.validate_admin_email`

**Parameters:**
```json
{
    "admin_email": "admin@example.com"
}
```

**Returns:**
```json
{
    "valid": true,
    "message": ""
}
```

## Validation Rules

### Institute Name
- Required: Yes
- Must be unique (no existing company with same name)
- Minimum length: 1 character
- Can contain spaces and special characters

### Institute Abbreviation
- Required: No (auto-generated if not provided)
- Must be unique if provided
- Pattern: Letters only, uppercase (e.g., MI, ABC123)
- Auto-generation: Uses first letter of each word, or first 2 letters

### Admin Email
- Required: Yes
- Must be valid email format
- Must be unique (no existing user with same email)
- Pattern: standard email format (user@domain.com)

### Admin Password
- Required: Yes
- Minimum length: 6 characters
- Stored securely using Frappe's password hashing

### Country
- Required: No (defaults to India)
- Must exist in Country DocType
- Examples: India, USA, Germany

### Currency
- Required: No (defaults to INR)
- Must exist in Currency DocType
- Must be enabled
- Examples: INR, USD, EUR

## Roles and Permissions

### System Manager
- Full access to all system settings
- User management
- Workspace and page configuration

### Institute Admin
- Full CRUD on all Education doctypes
- Student and Instructor management
- Course and Program management
- Assessment and Grading
- Fee management
- Attendance and Leave management
- Full access to all Vidyaan custom doctypes

## Error Handling

All setup functions include comprehensive error handling:

```python
try:
    setup_complete(args)
except frappe.ValidationError as e:
    frappe.log_error()
    frappe.msgprint(str(e))
except Exception as e:
    frappe.log_error()
    frappe.msgprint("Setup failed. Please check the error log.")
```

## Testing

Run the test suite:

```bash
# Test basic setup
bench --site yoursitename execute vidyaan.setup.test_setup.test_basic_setup

# Test full setup
bench --site yoursitename execute vidyaan.setup.test_setup.test_full_setup

# Test validation
bench --site yoursitename execute vidyaan.setup.test_setup.test_validation
```

## Troubleshooting

### Issue: "Institute name already exists"
**Solution:** Choose a unique institute name or delete the existing company

### Issue: "Email already in use"
**Solution:** Use a different email or delete the existing user

### Issue: "Abbreviation is already in use"
**Solution:** Provide a unique abbreviation or let the system auto-generate one

### Issue: "Setup already complete"
**Solution:** If setup is already complete and you need to restart, clear the `vidyaan_setup_complete` flag:
```python
frappe.defaults.delete_default("vidyaan_setup_complete")
```

### Issue: Password not being set
**Solution:** Ensure password is provided (minimum 6 characters) and Frappe's `update_password` function has proper permissions

## Advanced: Custom Setup Extensions

To add custom setup logic, create a hook in your module:

```python
# hooks.py
def after_setup():
    """Called after Vidyaan setup completes."""
    create_custom_data()
```

Then register in hooks:
```python
# In hooks.py
doc_events = {
    "Global Defaults": {
        "on_update": "your_module.after_setup"
    }
}
```

## Security Considerations

1. **Password Handling:**
   - Passwords are hashed using Frappe's secure hashing
   - Never store passwords in plain text
   - Use HTTPS when transmitting passwords over network

2. **Role Assignment:**
   - Admin user gets System Manager and Institute Admin roles
   - Additional roles can be assigned after setup
   - Permissions are enforced at DocType level

3. **Setup Completion:**
   - Setup should only be run once
   - Setup completion flag prevents re-running
   - Existing data is preserved

## Database Schema After Setup

After setup completes, the following records are created:

```
Company (Institute)
├── name: "Institute Name"
├── abbr: "IN"
├── country: "India"
└── currency: "INR"

User (Admin)
├── email: "admin@example.com"
├── first_name: "Administrator"
├── user_type: "System User"
└── roles: [System Manager, Institute Admin]

Global Defaults
├── default_company: "Institute Name"
├── default_currency: "INR"
└── country: "India"
```

## Related Documentation

- [Vidyaan Architecture](../../architecture.md)
- [Roles and Permissions](../roles.md)
- [Database Schema](../../database/doctype-map.md)
- [Frappe Setup Wizard](https://frappeframework.com)
