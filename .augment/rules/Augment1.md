---
type: "agent_requested"
description: "MCPs distributions"
---
# AUGMENT AI MANDATORY CHECKLIST

## 🚨 BEFORE STARTING ANY TASK - MANDATORY STEPS

### ✅ Step 1: CONTEXT LOADING (REQUIRED)
```
□ Identify task type from the table below
□ Read the PRIMARY agent documentation file
□ Read any SECONDARY agent files if applicable
□ Note the specific MCP tools mentioned in the docs
```

### ✅ Step 2: PATTERN IDENTIFICATION (REQUIRED)
```
□ Identify the exact architectural patterns to follow
□ Note the specific MCP tool integration patterns
□ Identify naming conventions and code organization
□ Note the error handling and monitoring patterns
```

### ✅ Step 3: IMPLEMENTATION (REQUIRED)
```
□ Use ONLY the patterns from agent documentation
□ Integrate the specified MCP tools exactly as shown
□ Follow the exact naming conventions
□ Implement the specified error handling
```

---

## 📋 QUICK TASK-TO-AGENT MAPPING

| **Task Type** | **Primary Agent** | **Secondary Agents** |
|---------------|------------------|---------------------|
| 🔌 API Development | `backend-api-developer.md` | `database-architect.md` |
| 🗄️ Database Work | `database-architect.md` | `data-engineer.md` |
| 🕷️ Web Scraping | `web-scraper.md` | `data-engineer.md` |
| 🎨 Frontend/UI | `frontend-developer.md` | `ui-ux-designer.md` |
| 📊 Data Processing | `data-engineer.md` | `database-architect.md` |
| ⚖️ Business Logic | `business-logic-agent.md` | `backend-api-developer.md` |
| 🔒 Security | `security-specialist.md` | `backend-api-developer.md` |
| 🧪 Testing/QA | `qa-tester.md` | `security-specialist.md` |
| 🚀 Infrastructure | `devops-infrastructure.md` | `database-architect.md` |
| 🎯 Product/Planning | `project-manager.md` | All technical agents |

---

## 🛠️ MCP TOOLS QUICK REFERENCE

### **Supabase MCP** (Database & Backend)
```javascript
// Use for: Database operations, migrations, edge functions
mcp__supabase__execute_sql()
mcp__supabase__apply_migration()
mcp__supabase__deploy_edge_function()
```

### **Playwright MCP** (Web Scraping)
```javascript
// Use for: Browser automation, scraping
mcp__playwright__browser_navigate()
mcp__playwright__browser_click()
mcp__playwright__browser_snapshot()
```

### **Context7 MCP** (Documentation)
```javascript
// Use for: Latest library documentation
mcp__context7__resolve_library_id()
mcp__context7__get_library_docs()
```

### **Exa MCP** (Research)
```javascript
// Use for: Web research, competitive analysis
mcp__exa__web_search_exa()
mcp__exa__deep_researcher_start()
```

### **IDE MCP** (Development Quality)
```javascript
// Use for: Code quality monitoring
mcp__ide__getDiagnostics()
mcp__ide__executeCode()
```

---

## ⚡ CRITICAL PATTERNS TO ALWAYS FOLLOW

### 🏗️ **Database Architecture**
- Use **Direct-to-Supabase** (NOT staging)
- Implement exact **15-field permit structure**
- Use **PostGIS for coordinates**
- Apply **Supabase MCP patterns**

### 🕷️ **Web Scraping Workflow**
- **Playwright MCP** as primary tool
- Follow: `Browser → Form → Search → Download → Extract → Store`
- Use **DATE-ONLY filtering** (01/01/2023 to current)
- Implement **exact error recovery patterns**

### 💰 **Pricing Calculations**
- **EXACT FORMULA**: `(Roundtrip Minutes × 1.83) + Added Minutes = Trucking Price/Load`
- **TOTAL**: `Dump Fee + Trucking Price/Load + LDP Fee = Total Price Per Load`

### 🎨 **Frontend Development**
- Use **Next.js** as primary framework
- Implement **Context7 MCP** for docs
- Follow **exact UI component patterns**
- Use **IDE MCP** for quality monitoring

---

## 🚨 VALIDATION BEFORE COMPLETION

### ✅ MANDATORY CHECKS
```
□ Implementation follows agent documentation patterns exactly
□ All specified MCP tools are integrated correctly
□ Naming conventions match agent standards
□ Error handling follows specified patterns
□ Architecture matches established patterns
□ Code includes comments referencing agent patterns followed
```

### 🔍 **Final Verification Questions**
1. **Did I read the relevant agent docs FIRST?**
2. **Am I using the exact patterns specified?**
3. **Are all MCP tools integrated correctly?**
4. **Does my code match the established architecture?**
5. **Have I followed the naming conventions?**

---

## ❌ COMMON MISTAKES TO AVOID

| ❌ **DON'T DO** | ✅ **DO THIS INSTEAD** |
|----------------|----------------------|
| Skip reading agent docs | ALWAYS read relevant agent docs first |
| Create new patterns | Use established patterns from docs |
| Ignore MCP integrations | Implement ALL specified MCP tools |
| Use different naming | Follow exact naming conventions |
| Skip error handling | Implement specified error patterns |

---

## 📍 FILE LOCATIONS

**Agent Documentation**: `.claude\agents\*.md`
**Rules Document**: `.claude\AUGMENT_AI_INTEGRATION_RULES.md`

---

**🎯 SUCCESS = Following agent patterns + MCP integrations + Quality standards**