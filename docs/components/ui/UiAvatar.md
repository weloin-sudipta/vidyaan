# UiAvatar

## Purpose
User avatar that shows a profile image when available, falling back to initials generated from the user's name.

## Location
`frontend/components/ui/UiAvatar.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `src` | `string` | — | Image URL (optional) |
| `name` | `string` | `''` | Used to generate initials fallback |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Avatar size |
| `alt` | `string` | — | Alt text for the image |

## Usage
```vue
<!-- With image -->
<UiAvatar :src="profile.user_image" :name="profile.full_name" size="lg" />

<!-- Initials fallback (no src) -->
<UiAvatar name="Sudipta Das" size="md" />
```

## Edge Cases
- If `src` is empty or fails to load, falls back to colored circle with initials
- Initials derived from first letter of each word in `name`, max 2 characters

## Notes
- Added in the 2026-04-08 UI primitives refactor
