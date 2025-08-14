---
type: "agent_requested"
description: "Guidelines"
---
# AUGMENT AI INSTRUCTION TEMPLATE

## 🚨 MANDATORY CONTEXT LOADING INSTRUCTION

**Copy and paste this instruction to Augment AI before every task:**

---

### BEFORE IMPLEMENTING ANYTHING:

1. **REQUIRED**: Read the relevant agent documentation from `.claude\agents\` directory:
   - Check `agent_integration_config.json` to determine which agent files to read
   - Read the PRIMARY agent documentation file completely
   - Read any SECONDARY agent files if applicable

2. **REQUIRED**: Follow the exact patterns and architectures specified in the agent docs:
   - Use the specified MCP tool integrations
   - Follow the established naming conventions  
   - Implement the exact error handling patterns
   - Use the specified architectural patterns

3. **REQUIRED**: For municipal permit system work, ensure:
   - Use the exact 15-field permit data structure
   - Implement the exact LDP pricing formula: (Roundtrip Minutes × 1.83) + Added Minutes
   - Follow the Direct-to-Supabase architecture (NOT staging approaches)
   - Use DATE-ONLY filtering for scraping (01/01/2023 to current date)

4. **VALIDATION**: Before considering the task complete:
   - Verify implementation matches agent documentation patterns
   - Confirm all specified MCP tools are integrated
   - Check that naming conventions are followed
   - Ensure error handling matches specifications

**Reference Files:**
- Agent docs: `.claude\agents\*.md`
- Rules: `.claude\AUGMENT_AI_INTEGRATION_RULES.md`
- Quick checklist: `.claude\AUGMENT_AI_CHECKLIST.md`
- Config mapping: `.claude\agent_integration_config.json`

---

**CRITICAL**: Implementation is only complete when it fully aligns with agent documentation patterns and includes all specified MCP tool integrations.

## TASK: [Insert your specific task here]

### CONTEXT: [Provide specific context about what needs to be implemented]

### REQUIREMENTS: [List specific requirements]

---

**Remember: Always read agent docs FIRST, then implement using the exact patterns specified.**