---
title: Typography System - Municipal Permit Tracking System
description: Comprehensive font hierarchy and responsive scaling for construction industry permit tracking interface with professional readability optimization
feature: design-system-typography
last-updated: 2025-01-15
version: 1.0.0
related-files:
  - ../style-guide.md
  - colors.md
  - spacing.md
dependencies:
  - Inter font family
  - JetBrains Mono for code elements
  - Responsive design requirements
status: draft
---

# Typography System - Municipal Permit Tracking System

## Typography Philosophy

The typography system prioritizes construction industry professionalism, permit data readability, and field operation optimization while maintaining clear information hierarchy across diverse device types and lighting conditions.

### Design Principles
- **Professional Readability**: Optimized for permit data scanning and technical information
- **Field Operation Clarity**: Enhanced legibility for outdoor construction environments
- **Information Hierarchy**: Clear distinction between permit data types and importance levels
- **Cross-Device Consistency**: Uniform reading experience from mobile to desktop
- **Accessibility First**: WCAG AA compliance with enhanced readability standards

## Font Stack

### Primary Font - Inter
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**Rationale:**
- **Professional Appearance**: Clean, modern sans-serif suitable for municipal data presentation
- **High Readability**: Optimized for screen reading with excellent character distinction
- **Comprehensive Character Set**: Full support for construction industry terminology and symbols
- **Variable Font Support**: Efficient loading and precise weight control
- **Cross-Platform Consistency**: Reliable rendering across construction industry devices

### Monospace Font - JetBrains Mono
```css
font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
```

**Usage:**
- Permit record numbers and identification codes
- Coordinate data and technical specifications
- Code snippets and API responses
- Precise data alignment in tables

## Font Weights

### Weight Scale
```css
--font-weight-light: 300;      /* Subtle text, secondary information */
--font-weight-regular: 400;    /* Body text, standard permit data */
--font-weight-medium: 500;     /* Emphasized text, form labels */
--font-weight-semibold: 600;   /* Section headers, important data */
--font-weight-bold: 700;       /* Page titles, critical information */
```

### Weight Usage Guidelines
- **Light (300)**: Subtle secondary information, metadata
- **Regular (400)**: Primary body text, permit descriptions, standard data
- **Medium (500)**: Form labels, emphasized text, navigation items
- **Semibold (600)**: Section headers, permit categories, important data
- **Bold (700)**: Page titles, critical alerts, primary headings

## Type Scale - Responsive Hierarchy

### Desktop Scale (1024px+)

#### Heading Hierarchy
```css
/* H1 - Page Titles, Main Permit Sections */
--font-h1-size: 32px;
--font-h1-line-height: 40px;
--font-h1-weight: 700;
--font-h1-letter-spacing: -0.02em;

/* H2 - Section Headers, Permit Categories */
--font-h2-size: 24px;
--font-h2-line-height: 32px;
--font-h2-weight: 600;
--font-h2-letter-spacing: -0.01em;

/* H3 - Subsection Headers, Permit Details */
--font-h3-size: 20px;
--font-h3-line-height: 28px;
--font-h3-weight: 600;
--font-h3-letter-spacing: 0;

/* H4 - Card Titles, Permit Identifiers */
--font-h4-size: 18px;
--font-h4-line-height: 24px;
--font-h4-weight: 500;
--font-h4-letter-spacing: 0;

/* H5 - Minor Headers, Field Labels */
--font-h5-size: 16px;
--font-h5-line-height: 20px;
--font-h5-weight: 500;
--font-h5-letter-spacing: 0;
```

#### Body Text Hierarchy
```css
/* Body Large - Primary Permit Descriptions */
--font-body-large-size: 18px;
--font-body-large-line-height: 28px;
--font-body-large-weight: 400;

/* Body - Standard Permit Data, Form Text */
--font-body-size: 16px;
--font-body-line-height: 24px;
--font-body-weight: 400;

/* Body Small - Secondary Information, Metadata */
--font-body-small-size: 14px;
--font-body-small-line-height: 20px;
--font-body-small-weight: 400;

/* Caption - Timestamps, Permit IDs */
--font-caption-size: 12px;
--font-caption-line-height: 16px;
--font-caption-weight: 400;
```

#### Specialized Text
```css
/* Label - Form Labels, Status Indicators */
--font-label-size: 14px;
--font-label-line-height: 16px;
--font-label-weight: 500;
--font-label-transform: uppercase;
--font-label-letter-spacing: 0.05em;

/* Code - Permit Numbers, Coordinates */
--font-code-size: 14px;
--font-code-line-height: 20px;
--font-code-weight: 400;
--font-code-family: var(--font-mono);
```

### Tablet Scale (768px-1023px)

#### Adjusted Heading Hierarchy
```css
/* H1 - Slightly reduced for tablet screens */
--font-h1-size-tablet: 28px;
--font-h1-line-height-tablet: 36px;

/* H2 - Optimized for tablet permit viewing */
--font-h2-size-tablet: 22px;
--font-h2-line-height-tablet: 28px;

/* H3 - Maintained readability */
--font-h3-size-tablet: 18px;
--font-h3-line-height-tablet: 24px;

/* Body - Optimized for tablet permit data */
--font-body-size-tablet: 16px;
--font-body-line-height-tablet: 24px;
```

### Mobile Scale (320px-767px)

#### Mobile-Optimized Hierarchy
```css
/* H1 - Mobile page titles */
--font-h1-size-mobile: 24px;
--font-h1-line-height-mobile: 32px;
--font-h1-weight-mobile: 700;

/* H2 - Mobile section headers */
--font-h2-size-mobile: 20px;
--font-h2-line-height-mobile: 28px;
--font-h2-weight-mobile: 600;

/* H3 - Mobile subsection headers */
--font-h3-size-mobile: 18px;
--font-h3-line-height-mobile: 24px;
--font-h3-weight-mobile: 600;

/* Body - Mobile permit data */
--font-body-size-mobile: 16px;
--font-body-line-height-mobile: 24px;
--font-body-weight-mobile: 400;

/* Body Small - Mobile secondary text */
--font-body-small-size-mobile: 14px;
--font-body-small-line-height-mobile: 20px;
```

## Typography Usage Guidelines

### Permit Data Hierarchy

#### Primary Permit Information
```css
.permit-title {
  font-size: var(--font-h3-size);
  line-height: var(--font-h3-line-height);
  font-weight: var(--font-h3-weight);
  color: var(--color-neutral-800);
}

.permit-id {
  font-family: var(--font-mono);
  font-size: var(--font-code-size);
  line-height: var(--font-code-line-height);
  color: var(--color-neutral-600);
}
```

#### Status and Category Labels
```css
.status-label {
  font-size: var(--font-label-size);
  line-height: var(--font-label-line-height);
  font-weight: var(--font-label-weight);
  text-transform: var(--font-label-transform);
  letter-spacing: var(--font-label-letter-spacing);
}
```

#### Permit Descriptions
```css
.permit-description {
  font-size: var(--font-body-size);
  line-height: var(--font-body-line-height);
  color: var(--color-neutral-600);
}

.permit-address {
  font-size: var(--font-body-small-size);
  line-height: var(--font-body-small-line-height);
  color: var(--color-neutral-500);
}
```

### Form Typography

#### Form Labels
```css
.form-label {
  font-size: var(--font-label-size);
  font-weight: var(--font-label-weight);
  color: var(--color-neutral-700);
  margin-bottom: 4px;
}
```

#### Input Fields
```css
.form-input {
  font-size: var(--font-body-size);
  line-height: var(--font-body-line-height);
  color: var(--color-neutral-800);
}

.form-input::placeholder {
  color: var(--color-neutral-400);
  font-weight: var(--font-weight-regular);
}
```

#### Help Text and Validation
```css
.form-help-text {
  font-size: var(--font-body-small-size);
  line-height: var(--font-body-small-line-height);
  color: var(--color-neutral-500);
}

.form-error-text {
  font-size: var(--font-body-small-size);
  line-height: var(--font-body-small-line-height);
  color: var(--color-error);
  font-weight: var(--font-weight-medium);
}
```

## Responsive Typography Implementation

### CSS Custom Properties
```css
:root {
  /* Desktop (default) */
  --font-h1: var(--font-h1-size) / var(--font-h1-line-height);
  --font-h2: var(--font-h2-size) / var(--font-h2-line-height);
  --font-body: var(--font-body-size) / var(--font-body-line-height);
}

/* Tablet breakpoint */
@media (max-width: 1023px) {
  :root {
    --font-h1: var(--font-h1-size-tablet) / var(--font-h1-line-height-tablet);
    --font-h2: var(--font-h2-size-tablet) / var(--font-h2-line-height-tablet);
  }
}

/* Mobile breakpoint */
@media (max-width: 767px) {
  :root {
    --font-h1: var(--font-h1-size-mobile) / var(--font-h1-line-height-mobile);
    --font-h2: var(--font-h2-size-mobile) / var(--font-h2-line-height-mobile);
    --font-body: var(--font-body-size-mobile) / var(--font-body-line-height-mobile);
  }
}
```

### Fluid Typography (Advanced)
```css
/* Fluid scaling between breakpoints */
.fluid-heading {
  font-size: clamp(
    var(--font-h1-size-mobile),
    4vw + 1rem,
    var(--font-h1-size)
  );
}
```

## Accessibility Standards

### WCAG AA Compliance
- **Line Height**: Minimum 1.5x font size for body text
- **Letter Spacing**: Minimum 0.12x font size for enhanced readability
- **Word Spacing**: Minimum 0.16x font size for improved scanning
- **Paragraph Spacing**: Minimum 2x font size for clear content separation

### Construction Industry Optimization
- **High Contrast**: Enhanced text contrast for outdoor visibility
- **Scalable Text**: Support for browser zoom up to 200% without horizontal scrolling
- **Clear Hierarchy**: Distinct size differences between heading levels
- **Readable Fonts**: Sans-serif fonts optimized for screen reading

## Performance Considerations

### Font Loading Strategy
```css
/* Font display optimization */
@font-face {
  font-family: 'Inter';
  font-display: swap;
  src: url('/fonts/inter-variable.woff2') format('woff2-variations');
}

/* Preload critical fonts */
<link rel="preload" href="/fonts/inter-variable.woff2" as="font" type="font/woff2" crossorigin>
```

### Variable Font Implementation
```css
/* Variable font axes */
.text-variable {
  font-variation-settings: 
    'wght' var(--font-weight-regular),
    'slnt' 0;
}
```

## Implementation Examples

### Permit Card Typography
```css
.permit-card {
  .permit-card__title {
    font: var(--font-h4-weight) var(--font-h4);
    color: var(--color-neutral-800);
  }
  
  .permit-card__id {
    font: var(--font-weight-regular) var(--font-code);
    color: var(--color-neutral-600);
  }
  
  .permit-card__status {
    font: var(--font-label-weight) var(--font-label);
    text-transform: var(--font-label-transform);
    letter-spacing: var(--font-label-letter-spacing);
  }
  
  .permit-card__description {
    font: var(--font-weight-regular) var(--font-body);
    color: var(--color-neutral-600);
  }
}
```

### Data Table Typography
```css
.data-table {
  .table-header {
    font: var(--font-label-weight) var(--font-label);
    color: var(--color-neutral-700);
  }
  
  .table-cell {
    font: var(--font-weight-regular) var(--font-body);
    color: var(--color-neutral-600);
  }
  
  .table-cell--numeric {
    font-family: var(--font-mono);
    text-align: right;
  }
}
```

## Related Documentation

- [Style Guide](../style-guide.md) - Complete design system overview
- [Color System](colors.md) - Text color usage and contrast standards
- [Spacing System](spacing.md) - Typography spacing and layout integration
- [Accessibility Guidelines](../../accessibility/guidelines.md) - Detailed accessibility standards

## Last Updated

**Change Log**:
- 2025-01-15: Complete typography system created with construction industry focus and responsive optimization
- Next: Spacing system development and component typography integration
