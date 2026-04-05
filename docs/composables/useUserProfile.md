# useUserProfile

## Purpose
User profile management composable handling profile data retrieval, updates, and avatar management for authenticated users.

## Location
`frontend/composable/useUserProfile.js`

## State Management

### Reactive State
```javascript
const profile = ref(null)        // User profile data
const loading = ref(false)       // Loading state
const error = ref(null)          // Error state
const updating = ref(false)      // Update operation state
```

### Profile Data Structure
```javascript
interface UserProfile {
  name: string           // Profile document name
  user: string           // Linked user ID
  first_name: string     // First name
  last_name: string      // Last name
  full_name: string      // Computed full name
  email: string          // Email address
  phone: string          // Phone number
  date_of_birth: string  // DOB (YYYY-MM-DD)
  gender: 'Male' | 'Female' | 'Other'
  address: string        // Full address
  city: string           // City
  state: string          // State
  country: string        // Country
  pincode: string        // Postal code
  user_image: string     // Profile image URL
  bio: string            // User biography
  emergency_contact: {
    name: string
    phone: string
    relation: string
  }
}
```

## API Methods

### fetchProfile()
Retrieves current user's profile data.

**Returns:** Promise<UserProfile>

### updateProfile(updates)
Updates user profile with provided data.

**Parameters:**
```javascript
Partial<UserProfile>  // Only fields to update
```

**Returns:** Promise<UserProfile>

### uploadAvatar(file)
Uploads and sets user profile image.

**Parameters:**
```javascript
File  // Image file object
```

**Returns:** Promise<{file_url: string}>

### updateEmergencyContact(contact)
Updates emergency contact information.

**Parameters:**
```javascript
{
  name: string
  phone: string
  relation: string
}
```

**Returns:** Promise<UserProfile>

## Usage Examples

### Profile Display
```javascript
const { profile, loading } = useUserProfile()

// Fetch on mount
onMounted(() => fetchProfile())

// Template
<div v-if="!loading && profile">
  <img :src="profile.user_image" class="avatar" />
  <h2>{{ profile.full_name }}</h2>
  <p>{{ profile.email }}</p>
  <p>{{ profile.bio }}</p>
</div>
```

### Profile Update Form
```javascript
const { updateProfile, updating } = useUserProfile()

const handleUpdate = async (formData) => {
  try {
    await updateProfile({
      first_name: formData.firstName,
      last_name: formData.lastName,
      phone: formData.phone,
      bio: formData.bio
    })
    showToast('Profile updated!')
  } catch (err) {
    showError('Update failed')
  }
}
```

### Avatar Upload
```javascript
const { uploadAvatar } = useUserProfile()

const handleAvatarUpload = async (file) => {
  try {
    const result = await uploadAvatar(file)
    // Avatar URL automatically updated in profile
    showToast('Avatar updated!')
  } catch (err) {
    showError('Upload failed')
  }
}
```

## Features

### Data Validation
- Email format validation
- Phone number format checking
- Required field validation
- Data type enforcement

### Image Management
- Automatic image upload to Frappe
- Image URL generation
- Avatar preview support
- File size/type validation

### Emergency Contact
- Separate contact management
- Relationship validation
- Contact information updates

### Reactive Updates
- Real-time profile state updates
- Cross-component synchronization
- Optimistic UI updates

## Dependencies
- useFrappeFetch for API calls
- useAuth for user context
- Vue 3 reactivity system

## Business Rules
- Profile data linked to User doctype
- Automatic full_name computation
- Address components for location services
- Emergency contact for safety features

## Error Cases
- Profile not found
- Validation failures
- Upload errors
- Permission denied
- Network failures