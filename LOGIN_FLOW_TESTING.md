# Login Flow Testing Guide

## Overview
The application now supports both **existing user login** and **new user onboarding** with a seamless flow that checks the SQLite database.

## Features Implemented

### Backend (MCP Server)
1. **New Endpoint**: `POST /api/user/login`
   - Accepts: `{"name": "username"}`
   - Returns: 
     - Existing user: `{"status": "success", "user": {...}, "is_existing": true}`
     - New user: `{"status": "success", "is_existing": false}`

2. **Database Function**: `get_user_by_name(name)` in `utils/database.py`
   - Case-insensitive name search
   - Returns most recent user if multiple exist
   - Handles NULL values for hobbies/interests

### Frontend (Angular)
1. **Two-Step Login Flow**:
   - **Step 1**: Enter name → System checks if user exists
   - **Step 2a**: Existing user → Redirect to dashboard
   - **Step 2b**: New user → Show onboarding form

2. **Updated Components**:
   - `login.component.ts`: Added `checkExistingUser()`, `toggleToNewUser()`, `backToLogin()` methods
   - `login.component.html`: Conditional UI for existing vs new users
   - `login.component.css`: Styles for divider and secondary button
   - `mcp.service.ts`: Added `loginUser()` method

## Testing Instructions

### Test 1: Existing User Login
1. Navigate to `http://localhost:4200`
2. Enter an existing username (e.g., "mounika" or "deep")
3. Click "🔍 Continue Investigation"
4. ✅ **Expected**: Redirects to dashboard with user data loaded

### Test 2: New User Onboarding
1. Navigate to `http://localhost:4200`
2. Enter a new username (e.g., "testuser123")
3. Click "🔍 Continue Investigation"
4. ✅ **Expected**: Shows onboarding form (age, hobbies, interests)
5. Complete the form and click "🔍 Start Investigation"
6. ✅ **Expected**: Creates profile and redirects to dashboard

### Test 3: Toggle Between Flows
1. Click "⭐ Join as New Detective" button
2. ✅ **Expected**: Shows onboarding form directly
3. Click "← Back to Login" button
4. ✅ **Expected**: Returns to simple name entry screen

### Test 4: Keyboard Navigation
1. Type your name in the input field
2. Press **Enter** key
3. ✅ **Expected**: Same behavior as clicking the button

## Existing Users in Database

Current test users available:
- **mounika** (age: 10, hobbies: music, art)
- **deep** (age: 10, multiple entries)

## API Endpoints

### Login Check
```bash
curl -X POST http://localhost:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"name": "mounika"}'
```

Response (existing user):
```json
{
  "status": "success",
  "user": {
    "user_id": "user_mounika",
    "name": "mounika",
    "age": 10,
    "hobbies": ["music", "art"],
    "interests": []
  },
  "is_existing": true
}
```

Response (new user):
```json
{
  "status": "success",
  "is_existing": false
}
```

## Technical Details

### Flow Diagram
```
1. User enters name
   ↓
2. Click "Continue Investigation"
   ↓
3. Frontend calls POST /api/user/login with name
   ↓
4. Backend queries SQLite database
   ↓
5a. User found → Return user data
    → Frontend loads gamification data
    → Navigate to /dashboard
    
5b. User not found → Return is_existing: false
    → Frontend shows onboarding form
    → User completes profile
    → Create new user in database
    → Navigate to /dashboard
```

### Database Query
The system uses a case-insensitive search:
```sql
SELECT * FROM users 
WHERE LOWER(name) = LOWER(?)
ORDER BY created_at DESC
LIMIT 1
```

## UI Features

### Login Screen (Existing User)
- Detective badge animation
- Single name input field
- "Continue Investigation" button (primary)
- "Join as New Detective" button (secondary)
- Divider with "OR" text

### Onboarding Screen (New User)
- Name field (pre-filled from step 1)
- Age selector (6-18)
- Hobbies selection (multiple)
- Interests selection (multiple)
- "Start Investigation" button (primary)
- "Back to Login" button (secondary)

## Success Criteria

✅ Existing users can login with just their name
✅ New users see onboarding form after name check
✅ Both flows successfully redirect to dashboard
✅ User data persists in SQLite database
✅ Gamification data loads correctly
✅ No duplicate user creation
✅ Case-insensitive name matching works
✅ NULL values handled gracefully

## Notes

- Name matching is case-insensitive
- If multiple users have the same name, the most recent is returned
- All routes already configured (login → dashboard flow exists)
- Session management uses BehaviorSubject in McpService
- Profile data stored in both currentUser$ and localStorage (implicit)
