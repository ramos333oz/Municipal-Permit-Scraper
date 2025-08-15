---
type: "agent_requested"
description: "Rules and Guidelines"
---
# Augment AI Integration Rules and Guidelines

## MANDATORY CONTEXT LOADING - CRITICAL REQUIREMENT

**RULE #1: ALWAYS READ RELEVANT AGENT DOCUMENTATION FIRST**
Before implementing ANY feature, functionality, or making ANY technical decisions, Augment AI MUST:

1. Refer to @Project_Guidelines.md and @Project_Overview to gain context on what you are actually working on. 

2. **Identify the Task Type** - Determine which specialized domain the task belongs to
3. **Load Relevant Agent Documentation** - Read the corresponding `.claude\agents\*.md` files
4. **Apply Agent Guidelines** - Follow the specific patterns, architectures, and MCP integrations defined in the agent docs
5. **Validate Against Standards** - Ensure implementation matches the established patterns

## Agent Documentation Directory Structure

```
.claude\agents\
├── backend-api-developer.md      # API development, Supabase integration
├── business-logic-agent.md       # Business rules, pricing calculations
├── data-engineer.md             # Data pipelines, ETL processes
├── database-architect.md        # PostgreSQL/PostGIS, Supabase schema
├── devops-infrastructure.md     # CI/CD, deployment, infrastructure
├── frontend-developer.md       # Next.js, React, mapping interfaces
├── project-manager.md          # Product specs, requirements
├── qa-tester.md                # Testing strategies, quality assurance
├── security-specialist.md      # Security analysis, vulnerability assessment
├── ui-ux-designer.md           # Interface design, user experience
└── web-scraper.md              # Municipal portal scraping, Playwright
```

## Task-to-Agent Mapping Rules

### ALWAYS use this mapping to determine which agent docs to read:

| Task Category | Primary Agent(s) | Secondary Agent(s) |
|---------------|------------------|-------------------|
| **API Development** | backend-api-developer | database-architect, security-specialist |
| **Database Operations** | database-architect | data-engineer, backend-api-developer |
| **Web Scraping** | web-scraper | data-engineer, backend-api-developer |
| **Frontend Development** | frontend-developer | ui-ux-designer, backend-api-developer |
| **Data Processing** | data-engineer | database-architect, business-logic-agent |
| **Business Logic** | business-logic-agent | backend-api-developer, data-engineer |
| **Security Analysis** | security-specialist | backend-api-developer, devops-infrastructure |
| **Testing/QA** | qa-tester | security-specialist, frontend-developer |
| **Infrastructure** | devops-infrastructure | database-architect, security-specialist |
| **UI/UX Design** | ui-ux-designer | frontend-developer, qa-tester |
| **Product Planning** | project-manager | All relevant technical agents |

## Mandatory Implementation Workflow

### Step 1: Context Loading (REQUIRED)
```
BEFORE writing ANY code:
1. Read the primary agent documentation file
2. If secondary agents are relevant, read their docs too
3. Note the specific MCP tool integrations available
4. Review the established patterns and architectures
```

### Step 2: Pattern Alignment (REQUIRED)
```
ENSURE your implementation:
1. Uses the exact same architectural patterns as the agent docs
2. Integrates with the specified MCP tools
3. Follows the established naming conventions
4. Matches the code organization structure
```

### Step 3: MCP Tool Integration (REQUIRED)
```
ALWAYS utilize the MCP tools specified in agent docs:
- Supabase MCP: For database operations, migrations, edge functions
- BROWSER MCP: For web scraping and automation
- Context7 MCP: For accessing latest documentation
- Exa MCP: For research and intelligence gathering
- IDE MCP: For development quality monitoring
- Shadcn MCP: For frontend UI and UX element and component easy integrations
```

## Specific Implementation Rules

### Database Operations
**RULE**: When implementing database features:
1. Read `database-architect.md` FIRST
2. Use the exact PostgreSQL/PostGIS schema patterns defined
3. Implement Supabase MCP integration as specified
4. Follow the Direct-to-Supabase architecture (NOT staging approaches)
5. Use the exact 15-field permit data structure

### Web Scraping Implementation
**RULE**: When implementing scraping features:
1. Read `web-scraper.md` FIRST
2. Use BROWSER MCP as the PRIMARY tool (with fallbacks as specified)
3. Follow the Browser→Form→Search→Download→Extract→Store workflow
4. Use DATE-ONLY filtering (avoid other filter types)
5. Implement the exact error recovery patterns

### API Development
**RULE**: When building APIs:
1. Read `backend-api-developer.md` FIRST
2. Use Supabase MCP for all database operations
3. Implement the exact LDP pricing formula: (Roundtrip Minutes × 1.83) + Added Minutes
4. Follow the development branch patterns for testing
5. Include comprehensive monitoring and logging

### Frontend Development
**RULE**: When building UI components:
1. Read `frontend-developer.md` FIRST
2. Use Next.js as the primary framework
3. Implement Context7 MCP for accessing latest docs
4. Follow the exact pricing calculation interfaces
5. Use IDE MCP for quality monitoring

## Quality Assurance Requirements

### Code Review Checklist
Before completing ANY implementation, verify:

- [ ] Relevant agent documentation was read and followed
- [ ] MCP tool integrations match the specified patterns
- [ ] Architecture follows the established patterns
- [ ] Naming conventions match the agent standards
- [ ] Error handling follows the specified patterns
- [ ] Performance optimizations are applied as specified
- [ ] Security measures match the agent requirements

### Validation Rules
**RULE**: Every implementation MUST:
1. Include comments referencing which agent patterns were followed
2. Use the exact same variable names and structure patterns
3. Implement the specified MCP tool integrations
4. Follow the established error handling patterns
5. Include the monitoring and logging patterns specified

## Error Prevention Rules

### Common Mistakes to AVOID:
1. **DON'T** implement without reading agent docs first
2. **DON'T** use different architectural patterns than specified
3. **DON'T** ignore MCP tool integrations
4. **DON'T** create new patterns when established ones exist
5. **DON'T** skip the quality assurance requirements

### Implementation Validation
**RULE**: Before considering any task complete:
1. Cross-reference implementation with agent documentation
2. Verify all MCP tools are properly integrated
3. Confirm patterns match the established standards
4. Test against the specified success criteria
5. Document which agent patterns were followed

## Municipal Permit System Specific Rules

### Data Structure Requirements
**RULE**: ALL permit data implementations MUST use the exact 15-field structure:
1. site_number, status, project_city, notes
2. project_company, project_contact, project_phone, project_email  
3. quantity, material_description
4. dump_fee, trucking_price_per_load, ldp_fee, total_price_per_load
5. Additional metadata fields as specified

### Pricing Calculation Requirements
**RULE**: ALL pricing calculations MUST use the exact formula:
- Trucking Price/Load = (Roundtrip Minutes × 1.83) + Added Minutes
- Total Price Per Load = Dump Fee + Trucking Price/Load + LDP Fee

### Scraping Requirements
**RULE**: ALL scraping implementations MUST:
- Use Playwright MCP as primary tool
- Follow the Browser→Form→Search→Download→Extract→Store workflow
- Use DATE-ONLY filtering (01/01/2023 to current date)
- Implement the exact error recovery patterns specified

## Enforcement and Monitoring

### Implementation Reviews
**MANDATORY**: Every implementation will be reviewed for:
1. Agent documentation compliance
2. MCP tool integration correctness
3. Pattern adherence
4. Quality standard compliance

### Continuous Alignment
**RULE**: If agent documentation is updated:
1. All future implementations MUST follow the updated patterns
2. Existing implementations should be flagged for potential updates
3. MCP tool integrations should be verified for currency

---

**CRITICAL REMINDER**: This document is not optional. Every implementation by Augment AI MUST follow these rules to ensure consistency, quality, and proper integration with the established municipal permit system architecture.

**SUCCESS CRITERIA**: Implementation is only considered complete when it fully aligns with the relevant agent documentation patterns and includes all specified MCP tool integrations.