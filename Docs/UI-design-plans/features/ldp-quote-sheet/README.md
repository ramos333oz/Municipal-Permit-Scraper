---
title: LDP Quote Sheet Interface - Municipal Permit Tracking System
description: Comprehensive UI/UX specifications for LDP Quote Sheet functionality including all 15 required data fields, pricing calculations, manual adjustments, and export capabilities
feature: ldp-quote-sheet
last-updated: 2025-01-15
version: 1.0.0
related-files:
  - user-journey.md
  - screen-states.md
  - pricing-calculations.md
  - export-functionality.md
dependencies:
  - Design system foundation
  - Business logic pricing formulas
  - Permit data structure (15 fields)
  - Export generation services
status: draft
---

# LDP Quote Sheet Interface - Municipal Permit Tracking System

## Feature Overview

The LDP Quote Sheet Interface provides construction professionals with comprehensive pricing calculation and quote generation capabilities for municipal permit projects. The interface handles all 15 required data fields, implements exact pricing formulas, and supports manual adjustments while maintaining professional presentation standards suitable for client delivery.

## Business Requirements

### Exact Pricing Formula Implementation
- **Trucking Price/Load**: (Roundtrip Minutes × 1.83) + Added Minutes
- **Total Price Per Load**: Dump Fee + Trucking Price/Load + LDP Fee
- **Real-time Calculations**: Dynamic updates as parameters change
- **Manual Adjustments**: Support for Added Minutes (5-30 min typical) and fee variations

### 15 Required Data Fields
1. **Core Permit Information**: Site Number, Status, Project City, Notes
2. **Contact Information**: Project Company, Project Contact, Project Phone, Project Email
3. **Material Details**: Quantity, Material Description
4. **Pricing Components**: Dump Fee, Trucking Price/Load, LDP Fee, Total Price/Load
5. **Additional Metadata**: Calculation details and timestamps

## User Experience Goals

### Primary Objectives
- **Accurate Quote Generation**: Professional-quality quote sheets with precise calculations
- **Efficient Data Entry**: Streamlined input process with validation and auto-completion
- **Real-time Calculations**: Immediate pricing updates as parameters change
- **Professional Export**: Multiple format options (PDF, Excel, CSV) for client delivery

### Success Metrics
- **Calculation Accuracy**: 100% precision in pricing formula implementation
- **Export Speed**: <5 seconds for complete quote sheet generation
- **Data Validation**: 95%+ accuracy in required field completion
- **User Efficiency**: 50% reduction in quote preparation time vs manual methods

## Interface Layout Structure

### Desktop Layout (1024px+)

#### Main Quote Sheet Panel
```css
.quote-sheet-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-6);
  padding: var(--spacing-6);
  max-width: 1200px;
  margin: 0 auto;
}

.quote-sheet-main {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-6);
}

.quote-sheet-sidebar {
  background: var(--color-neutral-50);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-5);
}
```

#### Section Organization
1. **Header Section**: Permit identification and status
2. **Contact Information**: Company and contact details
3. **Project Details**: Material type, quantity, and specifications
4. **Pricing Calculations**: Interactive calculation display
5. **Manual Adjustments**: Added minutes and fee modifications
6. **Export Controls**: Format selection and generation options

### Mobile Layout (320px-767px)

#### Responsive Adaptation
```css
@media (max-width: 767px) {
  .quote-sheet-container {
    grid-template-columns: 1fr;
    padding: var(--spacing-4);
  }
  
  .quote-sheet-section {
    margin-bottom: var(--spacing-5);
  }
}
```

## Core Interface Components

### 1. Permit Information Header

#### Visual Design
```css
.permit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  background: var(--color-primary-light);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-5);
}

.permit-id {
  font-family: var(--font-mono);
  font-size: var(--font-h4-size);
  font-weight: var(--font-weight-semibold);
  color: var(--color-neutral-800);
}

.permit-status {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--border-radius-full);
  font-size: var(--font-label-size);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: var(--font-label-letter-spacing);
}
```

#### Content Structure
- **Site Number**: Prominent display with copy-to-clipboard functionality
- **Status Badge**: Color-coded status indicator with last update timestamp
- **Project City**: Municipality information with compliance indicators
- **Quick Actions**: Edit, duplicate, archive options for admin users

### 2. Contact Information Section

#### Form Layout
```css
.contact-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-4);
  padding: var(--spacing-5);
  background: white;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--border-radius-md);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.form-label {
  font-size: var(--font-label-size);
  font-weight: var(--font-label-weight);
  color: var(--color-neutral-700);
}

.form-input {
  padding: var(--spacing-3) var(--spacing-4);
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-body-size);
  transition: border-color var(--duration-short) var(--ease-out);
}

.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-light);
  outline: none;
}
```

#### Field Specifications
- **Project Company**: Text input with auto-completion from previous entries
- **Project Contact**: Text input with name validation
- **Project Phone**: Formatted input with (XXX) XXX-XXXX pattern
- **Project Email**: Email input with validation and verification

### 3. Material and Quantity Section

#### Interactive Controls
```css
.material-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-4);
  align-items: end;
}

.quantity-input {
  position: relative;
}

.quantity-input input {
  text-align: right;
  font-family: var(--font-mono);
  font-size: var(--font-h4-size);
  font-weight: var(--font-weight-semibold);
}

.quantity-unit {
  position: absolute;
  right: var(--spacing-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-neutral-500);
  font-size: var(--font-body-small-size);
}
```

#### Content Elements
- **Material Description**: Dropdown with common construction materials
- **Quantity**: Numeric input with unit indicators (cubic yards, tons)
- **Material Notes**: Optional text area for specifications
- **Estimated Loads**: Auto-calculated based on quantity (10 CY per load assumption)

### 4. Pricing Calculation Display

#### Real-time Calculation Interface
```css
.pricing-calculator {
  background: var(--color-neutral-50);
  border: 2px solid var(--color-primary-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-5);
}

.calculation-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-2) 0;
  border-bottom: 1px solid var(--color-neutral-200);
}

.calculation-label {
  font-size: var(--font-body-size);
  color: var(--color-neutral-600);
}

.calculation-value {
  font-family: var(--font-mono);
  font-size: var(--font-body-size);
  font-weight: var(--font-weight-semibold);
  color: var(--color-neutral-800);
}

.calculation-total {
  background: var(--color-primary-light);
  margin: var(--spacing-3) calc(-1 * var(--spacing-5));
  padding: var(--spacing-3) var(--spacing-5);
  border-radius: var(--border-radius-md);
}

.calculation-total .calculation-value {
  font-size: var(--font-h4-size);
  color: var(--color-primary-dark);
}
```

#### Calculation Breakdown Display
1. **Roundtrip Minutes**: Calculated from coordinates with source indicator
2. **Base Calculation**: (Roundtrip Minutes × 1.83) with formula display
3. **Added Minutes**: Manual adjustment with typical range indicator
4. **Trucking Price/Load**: Calculated result with precision
5. **Additional Fees**: Dump Fee and LDP Fee with adjustment controls
6. **Total Price Per Load**: Final calculation with emphasis

### 5. Manual Adjustment Controls

#### Interactive Adjustment Panel
```css
.adjustment-panel {
  background: white;
  border: 1px solid var(--color-warning-light);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-4);
}

.adjustment-field {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-3);
}

.adjustment-input {
  width: 120px;
  text-align: center;
  font-family: var(--font-mono);
  font-weight: var(--font-weight-semibold);
}

.adjustment-slider {
  flex: 1;
  height: 6px;
  background: var(--color-neutral-200);
  border-radius: 3px;
  outline: none;
}

.adjustment-help {
  font-size: var(--font-body-small-size);
  color: var(--color-neutral-500);
  font-style: italic;
}
```

#### Adjustment Controls
- **Added Minutes**: Slider and input (0-60 min) with typical range guidance
- **Dump Fee**: Currency input with recent values dropdown
- **LDP Fee**: Currency input with project-specific adjustments
- **Override Toggle**: Option to manually override calculated values

### 6. Export and Action Controls

#### Export Options Interface
```css
.export-controls {
  display: flex;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background: var(--color-neutral-50);
  border-radius: var(--border-radius-md);
  border-top: 3px solid var(--color-success);
}

.export-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-short) var(--ease-out);
}

.export-button:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.export-icon {
  width: 20px;
  height: 20px;
}
```

#### Export Format Options
- **PDF Export**: Professional quote sheet with company branding
- **Excel Export**: Spreadsheet format with formulas and calculations
- **CSV Export**: Data format for integration with other systems
- **Email Direct**: Send quote sheet directly to project contact

## Data Validation and Error Handling

### Required Field Validation
```css
.form-field--required .form-label::after {
  content: " *";
  color: var(--color-error);
}

.form-input--error {
  border-color: var(--color-error);
  background-color: var(--color-error-light);
}

.form-error-message {
  font-size: var(--font-body-small-size);
  color: var(--color-error);
  margin-top: var(--spacing-1);
}
```

### Validation Rules
- **Site Number**: Required, unique identifier format
- **Contact Information**: Email format, phone number pattern
- **Quantity**: Positive number, reasonable range validation
- **Pricing Fields**: Non-negative currency values
- **Calculation Integrity**: Verify formula accuracy and prevent manipulation

## Accessibility Features

### Keyboard Navigation
- **Tab Order**: Logical progression through form fields
- **Keyboard Shortcuts**: Ctrl+E for export, Ctrl+S for save
- **Focus Indicators**: Clear visual focus for all interactive elements
- **Screen Reader Support**: ARIA labels and descriptions for calculations

### Visual Accessibility
- **High Contrast**: Enhanced contrast ratios for outdoor visibility
- **Large Touch Targets**: 44px minimum for mobile interactions
- **Clear Typography**: Professional fonts optimized for readability
- **Color Independence**: Status and validation not dependent on color alone

## Performance Optimization

### Real-time Calculations
- **Debounced Updates**: 300ms delay for input changes
- **Efficient Rendering**: Only update affected calculation components
- **Caching**: Store recent calculations for quick retrieval
- **Background Processing**: Complex calculations in web workers

### Export Performance
- **Template Caching**: Pre-compiled export templates
- **Streaming Generation**: Large exports with progress indicators
- **Format Optimization**: Efficient PDF and Excel generation
- **Client-side Processing**: Reduce server load for simple exports

## Related Documentation

- [User Journey](user-journey.md) - Complete user flow analysis
- [Screen States](screen-states.md) - All interface states and specifications
- [Pricing Calculations](pricing-calculations.md) - Detailed formula implementation
- [Export Functionality](export-functionality.md) - Export format specifications
- [Business Logic Agent](../../../.claude/agents/business-logic-agent.md) - Pricing formula requirements

## Implementation Notes

This quote sheet interface is optimized for:
- **Construction Industry Standards**: Professional presentation and accurate calculations
- **Municipal Compliance**: Proper data handling and audit trail maintenance
- **User Efficiency**: Streamlined workflows and automated calculations
- **Export Quality**: Professional-grade output suitable for client delivery
- **Next.js Integration**: Server-side rendering and API route optimization

## Last Updated

**Change Log**:
- 2025-01-15: Initial LDP Quote Sheet interface specifications created
- Next: Detailed user journey mapping and pricing calculation implementation
