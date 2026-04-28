# Phase 2: Brand Carousel & Single-Page Navigation

## Overview

This document captures the implementation details for adding a **brand carousel** and **single-page navigation** to the Byers Brands Web Portal homepage.

## Features Implemented

### 1. Brand Carousel (Ecosystem Projects)

**Location**: `apps/brand/templates/brand/home.html` - Products section

The carousel showcases all projects in the Byers Brands ecosystem:
- Project logo (or generated placeholder)
- Project name
- Brief description
- Link to project (opens in new tab)

**Technical Details**:
- Horizontally scrolling container with `overflow-x: auto` and `scroll-smooth`
- Snap scrolling with `snap-x snap-mandatory` for precise positioning
- Left/right arrow buttons for navigation
- Scroll indicator dots for direct access
- Touch-friendly for mobile devices

### 2. Project Data Model

**Location**: `apps/brand/models.py`

```python
class Project(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='project_logos/', blank=True)
    description = models.CharField(max_length=500)
    link = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
```

**Initial Data** (populated via migration `0003_populate_projects`):
1. Byers Brands Portal (featured)
2. Polly (featured)
3. Namechart (featured)
4. Cactus
5. Sonic

### 3. Single-Page Navigation

**Location**: `apps/core/templates/base.html`

Navigation links now use anchor links (`#home`, `#about`, `#products`, `#contact`) instead of separate page loads.

**Behavior**:
- Clicking nav items smoothly scrolls to the corresponding section
- Active section is highlighted in the navigation bar
- URL updates with hash (e.g., `#products`) without page reload
- Login, Register, and DID Login remain as separate pages

### 4. JavaScript Functionality

**Added to `home.html`**:

1. **Smooth Scrolling**: Intercepts anchor link clicks and uses `scrollIntoView({ behavior: 'smooth' })`
2. **Carousel Controls**: Left/right buttons scroll the track by 300px
3. **Scroll Indicators**: Updates active dot based on scroll position
4. **Active Nav Highlighting**: Updates nav link styling based on scroll position

## Files Modified

| File | Changes |
|------|---------|
| `apps/brand/models.py` | Added `Project` model |
| `apps/brand/views.py` | Updated `home()` to pass `projects` context |
| `apps/brand/templates/brand/home.html` | Added section IDs, brand carousel, JavaScript |
| `apps/core/templates/base.html` | Updated nav links to use `#` anchors |
| `apps/brand/migrations/0002_project.py` | Create Project model |
| `apps/brand/migrations/0003_populate_projects.py` | Populate initial project data |

## Testing

### Playwright Tests

**Location**: `tests/playwright/test_carousel_navigation.py`

Test coverage:
- Carousel exists with project cards
- Scroll buttons work correctly
- Horizontal scrolling is enabled
- Navigation links scroll to correct sections
- Active nav item updates on scroll
- Login/Register/DID Login link to separate pages
- Mobile responsiveness
- Project links open in new tab
- Carousel indicators are clickable

Run tests:
```bash
cd /home/user/CODE_BASE/byers_brands_portal
export DJANGO_SETTINGS_MODULE=config.settings.dev
uv run python manage.py runserver &  # Start server in background
uv run pytest tests/playwright/test_carousel_navigation.py -v
```

## Responsive Design

| Viewport | Behavior |
|----------|-----------|
| Mobile (< 640px) | Carousel scrollable with touch, 1 item visible at a time |
| Tablet (640-1024px) | 2-3 items visible in carousel |
| Desktop (> 1024px) | 3-4 items visible in carousel |

## Styling

- Brand color: `#0064aa`
- Dark mode support with Tailwind `dark:` classes
- Smooth transitions and hover effects
- Snap scrolling for precise carousel positioning

## Future Enhancements

To add a new project to the carousel:
1. Create a new `Project` object in Django admin or via shell
2. Set `order` for positioning
3. Upload logo to `project_logos/` directory
4. Set `is_featured=True` to highlight key projects

The carousel automatically accommodates new projects (up to a dozen+) without layout changes.

## Accessibility

- Carousel buttons have `aria-label` attributes
- Navigation has `role="navigation"` and `aria-label`
- Scroll indicators have `aria-label` for each dot
- Project links use `target="_blank"` with `rel="noopener noreferrer"`
- Semantic section IDs for anchor navigation
