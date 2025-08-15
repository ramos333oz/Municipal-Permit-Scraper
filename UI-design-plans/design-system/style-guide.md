---
title: Complete Style Guide - Municipal Permit Tracking System
description: Comprehensive design system specifications including colors, typography, spacing, components, and animations for construction industry permit tracking interface
feature: design-system
last-updated: 2025-01-15
version: 1.0.0
related-files:
  - tokens/colors.md
  - tokens/typography.md
  - tokens/spacing.md
  - tokens/animations.md
  - components/buttons.md
dependencies:
  - Construction industry UX research
  - Municipal compliance requirements
status: draft
---

# Complete Style Guide - Municipal Permit Tracking System

## Design Philosophy

This style guide embodies construction industry professionalism with field operation optimization, creating interfaces that feel effortless for permit tracking while maintaining municipal compliance across 35-40 Southern California cities.

### Core Design Principles

- **Bold simplicity** with intuitive navigation creating frictionless permit discovery workflows
- **Breathable whitespace** complemented by strategic color accents for permit status hierarchy
- **Strategic negative space** calibrated for cognitive breathing room and permit data prioritization
- **Systematic color theory** applied through permit status indicators and municipal compliance coding
- **Typography hierarchy** utilizing weight variance for permit information architecture
- **Visual density optimization** balancing permit data availability with cognitive load management
- **Motion choreography** implementing physics-based transitions for map interactions and status updates
- **Accessibility-driven** contrast ratios ensuring outdoor visibility and universal usability
- **Feedback responsiveness** via permit status transitions communicating system changes with minimal latency
- **Content-first layouts** prioritizing permit data and construction workflows over decorative elements

## 1. Color System

### Primary Colors - Construction Industry Professional
- **Primary**: `#2563EB` – Main CTAs, permit actions, primary navigation
- **Primary Dark**: `#1D4ED8` – Hover states, active permit selections
- **Primary Light**: `#DBEAFE` – Subtle backgrounds, permit highlights

### Secondary Colors - Municipal Compliance
- **Secondary**: `#64748B` – Supporting elements, secondary navigation
- **Secondary Light**: `#F1F5F9` – Background sections, card containers
- **Secondary Pale**: `#F8FAFC` – Selected states, hover backgrounds

### Permit Status Colors - Construction Workflow
- **Active Permit**: `#059669` – Open permits available for construction
- **HOT Permit**: `#DC2626` – High-priority permits requiring immediate attention
- **Completed**: `#6B7280` – Finished permits for historical reference
- **Under Review**: `#D97706` – Permits pending municipal approval
- **Inactive**: `#9CA3AF` – Permits no longer valid for construction

### Semantic Colors - System Feedback
- **Success**: `#10B981` – Successful permit updates, export completion
- **Warning**: `#F59E0B` – Caution states, data quality alerts
- **Error**: `#EF4444` – Errors, failed operations, validation issues
- **Info**: `#3B82F6` – Informational messages, system notifications

### Neutral Palette - Data Display
- `Neutral-50`: `#F9FAFB` – Lightest backgrounds
- `Neutral-100`: `#F3F4F6` – Card backgrounds
- `Neutral-200`: `#E5E7EB` – Borders, dividers
- `Neutral-300`: `#D1D5DB` – Disabled states
- `Neutral-400`: `#9CA3AF` – Placeholder text
- `Neutral-500`: `#6B7280` – Secondary text
- `Neutral-600`: `#4B5563` – Primary text
- `Neutral-700`: `#374151` – Headings
- `Neutral-800`: `#1F2937` – Dark text
- `Neutral-900`: `#111827` – Darkest text

### Accessibility Notes
- All color combinations meet WCAG AA standards (4.5:1 normal text, 3:1 large text)
- Critical permit status indicators maintain 7:1 contrast ratio for enhanced outdoor visibility
- Color-blind friendly palette with shape and icon reinforcement for permit status

## 2. Typography System

### Font Stack - Professional Construction Industry
- **Primary**: `Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif`
- **Monospace**: `JetBrains Mono, Consolas, Monaco, monospace`

### Font Weights
- Light: 300, Regular: 400, Medium: 500, Semibold: 600, Bold: 700

### Type Scale - Permit Data Hierarchy

#### Desktop Scale
- **H1**: `32px/40px, 700, -0.02em` – Page titles, main permit sections
- **H2**: `24px/32px, 600, -0.01em` – Section headers, permit categories
- **H3**: `20px/28px, 600, 0` – Subsection headers, permit details
- **H4**: `18px/24px, 500, 0` – Card titles, permit identifiers
- **H5**: `16px/20px, 500, 0` – Minor headers, field labels
- **Body Large**: `18px/28px, 400` – Primary permit descriptions
- **Body**: `16px/24px, 400` – Standard permit data, form text
- **Body Small**: `14px/20px, 400` – Secondary information, metadata
- **Caption**: `12px/16px, 400` – Timestamps, permit IDs
- **Label**: `14px/16px, 500, uppercase` – Form labels, status indicators
- **Code**: `14px/20px, 400, monospace` – Permit numbers, coordinates

#### Mobile Scale (320px-767px)
- **H1**: `28px/36px, 700, -0.02em`
- **H2**: `22px/28px, 600, -0.01em`
- **H3**: `18px/24px, 600, 0`
- **Body**: `16px/24px, 400` – Optimized for mobile permit viewing
- **Body Small**: `14px/20px, 400`

## 3. Spacing & Layout System

### Base Unit: `8px` (Construction Industry Standard)

### Spacing Scale
- `xs`: 4px – Micro spacing between related permit elements
- `sm`: 8px – Small spacing, internal card padding
- `md`: 16px – Default spacing, standard margins between permit sections
- `lg`: 24px – Medium spacing between permit categories
- `xl`: 32px – Large spacing, major section separation
- `2xl`: 48px – Extra large spacing, page section padding
- `3xl`: 64px – Huge spacing, hero sections, map containers

### Grid System - Responsive Permit Layout
- **Columns**: 12 (desktop), 8 (tablet), 4 (mobile)
- **Gutters**: 24px (desktop), 16px (tablet), 12px (mobile)
- **Margins**: 24px (desktop), 16px (tablet), 12px (mobile)
- **Container max-widths**: 1200px (desktop), 768px (tablet), 100% (mobile)

### Breakpoints - Construction Device Optimization
- **Mobile**: 320px – 767px (Field smartphones)
- **Tablet**: 768px – 1023px (Field tablets, vehicle-mounted devices)
- **Desktop**: 1024px – 1439px (Office workstations)
- **Wide**: 1440px+ (Large office displays, project rooms)

## 4. Component Specifications

### Button Components

#### Primary Button - Permit Actions
**Variants**: Primary, Secondary, Tertiary, Ghost
**States**: Default, Hover, Active, Focus, Disabled, Loading

**Visual Specifications**:
- **Height**: `44px` (touch-friendly for field operations)
- **Padding**: `12px 24px` internal spacing
- **Border Radius**: `8px` modern, professional appearance
- **Border**: `2px solid transparent` (focus: `2px solid #2563EB`)
- **Shadow**: `0 1px 2px rgba(0, 0, 0, 0.05)` subtle elevation
- **Typography**: Body Medium (16px/24px, 500)

**Interaction Specifications**:
- **Hover Transition**: `150ms ease-out` with background color change
- **Click Feedback**: Scale transform `scale(0.98)` for 100ms
- **Focus Indicator**: 2px blue outline with 2px offset for accessibility
- **Loading State**: Spinner animation with disabled interaction
- **Disabled State**: 50% opacity with no hover effects

### Form Components

#### Input Fields - Permit Data Entry
**Variants**: Text, Number, Email, Phone, Select, Textarea
**States**: Default, Focus, Error, Success, Disabled

**Visual Specifications**:
- **Height**: `44px` (single line), `88px` (textarea)
- **Padding**: `12px 16px`
- **Border**: `1px solid #D1D5DB` (focus: `2px solid #2563EB`)
- **Border Radius**: `6px`
- **Typography**: Body (16px/24px, 400)

### Map Components

#### Permit Markers - Location Indicators
**Variants**: Active, HOT, Completed, Under Review, Inactive
**States**: Default, Hover, Selected, Clustered

**Visual Specifications**:
- **Size**: `32px × 32px` (individual), `48px × 48px` (clustered)
- **Colors**: Status-specific (Active: #059669, HOT: #DC2626, etc.)
- **Icon**: Construction-themed icons (hard hat, excavator, etc.)
- **Shadow**: `0 2px 4px rgba(0, 0, 0, 0.2)` for map visibility

## 5. Motion & Animation System

### Timing Functions - Construction Industry Appropriate
- **Ease-out**: `cubic-bezier(0.0, 0, 0.2, 1)` – Map entrances, permit loading
- **Ease-in-out**: `cubic-bezier(0.4, 0, 0.6, 1)` – Status transitions, navigation
- **Spring**: `cubic-bezier(0.68, -0.55, 0.265, 1.55)` – Success feedback, permit updates

### Duration Scale
- **Micro**: 100ms – Permit status changes, hover effects
- **Short**: 200ms – Local transitions, dropdown menus
- **Medium**: 400ms – Map transitions, modal appearances
- **Long**: 600ms – Complex permit data loading, route calculations

### Animation Principles
- **Performance**: 60fps minimum, hardware acceleration for map interactions
- **Purpose**: Every animation serves permit workflow functionality
- **Consistency**: Similar permit actions use similar timings and easing
- **Accessibility**: Respect `prefers-reduced-motion` for construction users

## 6. Accessibility Standards

### WCAG AA Compliance
- **Color Contrast**: 4.5:1 minimum for permit text, 3:1 for large permit headers
- **Keyboard Navigation**: Complete permit management without mouse
- **Screen Reader Support**: Semantic HTML and ARIA labels for permit data
- **Touch Targets**: 44×44px minimum for field operation compatibility

### Construction Industry Accessibility
- **Outdoor Visibility**: High contrast mode for sunlight readability
- **Work Glove Compatibility**: Larger touch targets and simplified gestures
- **Cognitive Load**: Progressive disclosure of complex permit information
- **Multi-language**: Spanish language support for diverse construction teams

## Implementation Guidelines

### Next.js Integration
- **CSS Modules**: Component-scoped styling for permit interfaces
- **Tailwind CSS**: Utility-first approach with custom permit status classes
- **CSS-in-JS**: Dynamic styling for real-time permit status updates
- **Performance**: Optimized CSS delivery and critical path rendering

### Component Development
- **Atomic Design**: Design tokens → atoms → molecules → organisms → templates
- **TypeScript**: Full type safety for permit data structures and component props
- **Storybook**: Component documentation and testing environment
- **Testing**: Unit tests for component behavior and accessibility compliance

## Quality Assurance Checklist

### Design System Compliance
- [ ] Colors match defined palette with proper contrast ratios for outdoor use
- [ ] Typography follows established hierarchy and construction industry readability
- [ ] Spacing uses systematic scale consistently across permit interfaces
- [ ] Components match documented specifications for field operation compatibility
- [ ] Motion follows timing and easing standards for professional workflows

### Construction Industry Validation
- [ ] Permit workflows clearly supported throughout interface design
- [ ] Navigation intuitive for construction professionals with varying technical skills
- [ ] Error states provide clear guidance for permit data correction
- [ ] Loading states communicate progress for large permit dataset operations
- [ ] Success states provide clear confirmation for permit updates and exports

## Related Documentation

- [Color System](tokens/colors.md) - Detailed color specifications and usage
- [Typography System](tokens/typography.md) - Complete font hierarchy and responsive scaling
- [Component Library](components/) - Individual component specifications
- [Feature Specifications](../features/) - Application-specific design patterns

## Implementation Notes

This style guide is optimized for:
- **Construction Industry Workflows**: Professional permit tracking and quote generation
- **Municipal Compliance**: Consistent data presentation across 35-40 cities
- **Field Operations**: Mobile and tablet optimization for outdoor construction use
- **Kombai AI Compatibility**: Structured for efficient design-to-code conversion

## Last Updated

**Change Log**:
- 2025-01-15: Complete style guide foundation created with construction industry focus
- Next: Individual component specifications and feature interface design
