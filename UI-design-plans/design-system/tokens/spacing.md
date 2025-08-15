---
title: Spacing & Layout System - Municipal Permit Tracking System
description: Comprehensive spacing scale and grid system for construction industry permit tracking interface with touch-friendly optimization
feature: design-system-spacing
last-updated: 2025-01-15
version: 1.0.0
related-files:
  - ../style-guide.md
  - colors.md
  - typography.md
dependencies:
  - 8px base unit system
  - Responsive design requirements
  - Touch target accessibility standards
status: draft
---

# Spacing & Layout System - Municipal Permit Tracking System

## Spacing Philosophy

The spacing system prioritizes construction industry workflows, touch-friendly interactions, and efficient permit data organization while maintaining visual clarity across diverse device types and field operation contexts.

### Design Principles
- **Touch-Friendly Spacing**: Optimized for field operations with work gloves and mobile devices
- **Information Density**: Balanced spacing for permit data scanning and cognitive processing
- **Systematic Consistency**: Mathematical progression ensuring visual harmony
- **Responsive Adaptation**: Fluid spacing that adapts to different screen sizes and orientations
- **Accessibility Compliance**: Adequate spacing for users with motor impairments

## Base Unit System

### Foundation: 8px Base Unit
```css
--spacing-base: 8px;
```

**Rationale:**
- **Mathematical Consistency**: Clean multiplication for systematic spacing relationships
- **Device Compatibility**: Aligns with common screen pixel densities and touch targets
- **Construction Industry Standards**: Appropriate scale for professional interface density
- **Accessibility**: Supports minimum touch target requirements (44px = 5.5 × base unit)

## Spacing Scale

### Core Spacing Values
```css
--spacing-xs: 4px;      /* 0.5 × base - Micro spacing between related elements */
--spacing-sm: 8px;      /* 1 × base - Small spacing, internal padding */
--spacing-md: 16px;     /* 2 × base - Default spacing, standard margins */
--spacing-lg: 24px;     /* 3 × base - Medium spacing between sections */
--spacing-xl: 32px;     /* 4 × base - Large spacing, major section separation */
--spacing-2xl: 48px;    /* 6 × base - Extra large spacing, screen padding */
--spacing-3xl: 64px;    /* 8 × base - Huge spacing, hero sections */
--spacing-4xl: 96px;    /* 12 × base - Maximum spacing, page-level separation */
```

### Extended Spacing Values
```css
--spacing-0: 0px;       /* No spacing */
--spacing-1: 2px;       /* 0.25 × base - Minimal spacing, borders */
--spacing-2: 4px;       /* 0.5 × base - Micro spacing */
--spacing-3: 8px;       /* 1 × base - Small spacing */
--spacing-4: 16px;      /* 2 × base - Default spacing */
--spacing-5: 24px;      /* 3 × base - Medium spacing */
--spacing-6: 32px;      /* 4 × base - Large spacing */
--spacing-8: 48px;      /* 6 × base - Extra large spacing */
--spacing-10: 64px;     /* 8 × base - Huge spacing */
--spacing-12: 96px;     /* 12 × base - Maximum spacing */
```

## Spacing Usage Guidelines

### Component Internal Spacing

#### Button Padding
```css
/* Touch-friendly button padding for field operations */
.btn-small { padding: var(--spacing-2) var(--spacing-3); }    /* 4px 8px */
.btn-medium { padding: var(--spacing-3) var(--spacing-4); }   /* 8px 16px */
.btn-large { padding: var(--spacing-4) var(--spacing-5); }    /* 16px 24px */
```

#### Card Padding
```css
/* Permit card internal spacing */
.card-compact { padding: var(--spacing-3); }                 /* 8px */
.card-default { padding: var(--spacing-4); }                 /* 16px */
.card-comfortable { padding: var(--spacing-5); }             /* 24px */
.card-spacious { padding: var(--spacing-6); }                /* 32px */
```

#### Form Element Spacing
```css
/* Form field internal padding */
.form-input { 
  padding: var(--spacing-3) var(--spacing-4);                /* 8px 16px */
  margin-bottom: var(--spacing-4);                           /* 16px */
}

.form-label { 
  margin-bottom: var(--spacing-1);                           /* 2px */
}

.form-group { 
  margin-bottom: var(--spacing-5);                           /* 24px */
}
```

### Layout Spacing

#### Section Separation
```css
/* Major page sections */
.section-spacing-small { margin-bottom: var(--spacing-5); }   /* 24px */
.section-spacing-medium { margin-bottom: var(--spacing-6); }  /* 32px */
.section-spacing-large { margin-bottom: var(--spacing-8); }   /* 48px */
.section-spacing-huge { margin-bottom: var(--spacing-10); }   /* 64px */
```

#### Content Spacing
```css
/* Permit data content spacing */
.content-spacing-tight { gap: var(--spacing-2); }            /* 4px */
.content-spacing-normal { gap: var(--spacing-4); }           /* 16px */
.content-spacing-loose { gap: var(--spacing-5); }            /* 24px */
```

#### List and Grid Spacing
```css
/* Permit list and grid spacing */
.list-spacing { gap: var(--spacing-3); }                     /* 8px */
.grid-spacing-compact { gap: var(--spacing-4); }             /* 16px */
.grid-spacing-comfortable { gap: var(--spacing-5); }         /* 24px */
```

## Grid System

### Responsive Grid Configuration

#### Desktop Grid (1024px+)
```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-5);                                      /* 24px */
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-5);                                /* 24px */
}
```

#### Tablet Grid (768px-1023px)
```css
@media (max-width: 1023px) {
  .grid-container {
    grid-template-columns: repeat(8, 1fr);
    gap: var(--spacing-4);                                    /* 16px */
    padding: 0 var(--spacing-4);                              /* 16px */
  }
}
```

#### Mobile Grid (320px-767px)
```css
@media (max-width: 767px) {
  .grid-container {
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-3);                                    /* 8px */
    padding: 0 var(--spacing-3);                              /* 8px */
  }
}
```

### Grid Utilities

#### Column Spans
```css
/* Desktop column spans */
.col-1 { grid-column: span 1; }
.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-8 { grid-column: span 8; }
.col-12 { grid-column: span 12; }

/* Responsive column spans */
@media (max-width: 1023px) {
  .col-tablet-4 { grid-column: span 4; }
  .col-tablet-8 { grid-column: span 8; }
}

@media (max-width: 767px) {
  .col-mobile-2 { grid-column: span 2; }
  .col-mobile-4 { grid-column: span 4; }
}
```

## Responsive Spacing

### Breakpoint-Specific Spacing

#### Mobile Spacing Adjustments
```css
@media (max-width: 767px) {
  :root {
    --spacing-section-mobile: var(--spacing-4);              /* 16px */
    --spacing-card-mobile: var(--spacing-3);                 /* 8px */
    --spacing-button-mobile: var(--spacing-3);               /* 8px */
  }
  
  .section-spacing { margin-bottom: var(--spacing-section-mobile); }
  .card-padding { padding: var(--spacing-card-mobile); }
}
```

#### Tablet Spacing Adjustments
```css
@media (min-width: 768px) and (max-width: 1023px) {
  :root {
    --spacing-section-tablet: var(--spacing-5);              /* 24px */
    --spacing-card-tablet: var(--spacing-4);                 /* 16px */
  }
  
  .section-spacing { margin-bottom: var(--spacing-section-tablet); }
  .card-padding { padding: var(--spacing-card-tablet); }
}
```

### Fluid Spacing
```css
/* Fluid spacing using clamp() for smooth transitions */
.fluid-spacing {
  padding: clamp(
    var(--spacing-3),                                         /* 8px minimum */
    4vw,                                                      /* 4% of viewport width */
    var(--spacing-6)                                          /* 32px maximum */
  );
}
```

## Touch Target Standards

### Minimum Touch Targets
```css
/* Construction industry touch target standards */
--touch-target-minimum: 44px;                                /* WCAG AA minimum */
--touch-target-comfortable: 48px;                            /* Recommended for field use */
--touch-target-large: 56px;                                  /* Work glove friendly */
```

### Touch Target Implementation
```css
.touch-target {
  min-height: var(--touch-target-minimum);
  min-width: var(--touch-target-minimum);
  padding: var(--spacing-3) var(--spacing-4);
}

.touch-target--comfortable {
  min-height: var(--touch-target-comfortable);
  min-width: var(--touch-target-comfortable);
}

.touch-target--large {
  min-height: var(--touch-target-large);
  min-width: var(--touch-target-large);
}
```

## Permit-Specific Spacing Patterns

### Permit Card Layout
```css
.permit-card {
  padding: var(--spacing-4);                                 /* 16px */
  margin-bottom: var(--spacing-3);                           /* 8px */
  gap: var(--spacing-3);                                     /* 8px between elements */
}

.permit-card__header {
  margin-bottom: var(--spacing-2);                           /* 4px */
}

.permit-card__content {
  margin-bottom: var(--spacing-3);                           /* 8px */
}

.permit-card__actions {
  margin-top: var(--spacing-4);                              /* 16px */
  gap: var(--spacing-2);                                     /* 4px between buttons */
}
```

### Map Interface Spacing
```css
.map-container {
  padding: var(--spacing-4);                                 /* 16px */
}

.map-controls {
  gap: var(--spacing-2);                                     /* 4px */
  padding: var(--spacing-3);                                 /* 8px */
}

.map-popup {
  padding: var(--spacing-3);                                 /* 8px */
  margin: var(--spacing-2);                                  /* 4px */
}
```

### Data Table Spacing
```css
.data-table {
  border-spacing: 0;
}

.data-table th,
.data-table td {
  padding: var(--spacing-3) var(--spacing-4);                /* 8px 16px */
}

.data-table tbody tr {
  border-bottom: 1px solid var(--color-neutral-200);
}
```

## Accessibility Considerations

### Motor Impairment Support
- **Adequate Spacing**: Minimum 8px between interactive elements
- **Touch Target Size**: 44px minimum for all clickable elements
- **Clear Separation**: Visual spacing between different content areas
- **Consistent Patterns**: Predictable spacing for muscle memory

### Cognitive Load Management
- **Information Grouping**: Related permit data grouped with consistent spacing
- **Visual Hierarchy**: Spacing reinforces content importance and relationships
- **Breathing Room**: Adequate whitespace prevents visual overwhelm
- **Scannable Layout**: Consistent spacing patterns aid in quick information scanning

## Implementation Examples

### CSS Utility Classes
```css
/* Margin utilities */
.m-0 { margin: 0; }
.m-1 { margin: var(--spacing-1); }
.m-2 { margin: var(--spacing-2); }
.m-3 { margin: var(--spacing-3); }
.m-4 { margin: var(--spacing-4); }

/* Padding utilities */
.p-0 { padding: 0; }
.p-1 { padding: var(--spacing-1); }
.p-2 { padding: var(--spacing-2); }
.p-3 { padding: var(--spacing-3); }
.p-4 { padding: var(--spacing-4); }

/* Gap utilities for flexbox and grid */
.gap-1 { gap: var(--spacing-1); }
.gap-2 { gap: var(--spacing-2); }
.gap-3 { gap: var(--spacing-3); }
.gap-4 { gap: var(--spacing-4); }
```

### Component Spacing Examples
```css
/* Permit list component */
.permit-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);                                     /* 8px between items */
  padding: var(--spacing-4);                                 /* 16px container padding */
}

/* Form layout */
.form-layout {
  display: grid;
  gap: var(--spacing-5);                                     /* 24px between form sections */
  padding: var(--spacing-6);                                 /* 32px form padding */
}
```

## Performance Considerations

### CSS Custom Properties
```css
/* Efficient spacing value management */
:root {
  --spacing-scale: 8px;
  --spacing-xs: calc(var(--spacing-scale) * 0.5);
  --spacing-sm: calc(var(--spacing-scale) * 1);
  --spacing-md: calc(var(--spacing-scale) * 2);
  --spacing-lg: calc(var(--spacing-scale) * 3);
}
```

### Responsive Spacing Optimization
```css
/* Container queries for component-level responsive spacing */
@container (max-width: 400px) {
  .permit-card {
    padding: var(--spacing-3);                               /* Reduced padding in small containers */
  }
}
```

## Related Documentation

- [Style Guide](../style-guide.md) - Complete design system overview
- [Typography System](typography.md) - Text spacing and line height standards
- [Component Library](../components/) - Component-specific spacing applications
- [Accessibility Guidelines](../../accessibility/guidelines.md) - Spacing accessibility standards

## Last Updated

**Change Log**:
- 2025-01-15: Complete spacing and layout system created with construction industry focus and touch-friendly optimization
- Next: Animation system development and component spacing integration
