# What's Next

**Current Status**: Phase 3 In Progress
**Last Updated**: 2025-11-24
**Previous**: See `PHASE_3_PROGRESS.md` for what was just built

---

## Where We Left Off

The conversational AI layer is working. Echo can chat with users, understand their data, and explain metrics in plain English.

**What's done:**
- Chat endpoints (send messages, load data, manage sessions)
- Echo persona (McKinsey-style consultant)
- Data context injection (auto-calculates metrics when you upload)
- Session management (maintains conversation history)
- 31 tests, 99% coverage on conversation service

You can now have a natural conversation about your business data.

---

## What We Need to Do Next

The conversation works, but we're still missing structured reports. Right now Echo gives ad-hoc answers. We need it to also generate proper reports.

### Task 1: Report Templates

Create predefined report formats that combine multiple metrics into a cohesive story.

**Templates to build:**
1. **Weekly Revenue Health**
   - Total revenue, growth rate, MRR, ARR
   - Revenue by product breakdown
   - Key trends and concerns

2. **Marketing Funnel Performance**
   - Conversion rate, funnel analysis
   - Channel performance comparison
   - Optimization opportunities

3. **Financial Overview**
   - CAC, LTV, LTV:CAC ratio
   - Burn rate, runway
   - Unit economics assessment

Each template should define:
- Required metrics
- Required data columns
- Narrative sections (executive summary, findings, recommendations)

**Files to create:**
```
app/services/reports/
├── __init__.py
├── templates.py      # Template definitions
└── generator.py      # Report generation logic
```

### Task 2: Report Generation Endpoint

Build the API to generate reports from templates.

```
POST /api/v1/reports/generate
  - template_type: "revenue_health" | "marketing_funnel" | "financial_overview"
  - file: CSV upload

Returns:
  - report_id
  - metrics (all calculated values)
  - narratives (LLM-generated sections)
```

This combines:
1. Calculate all required metrics (deterministic)
2. Generate narrative sections (LLM)
3. Format into structured report

### Task 3: Report Storage

Save generated reports to PostgreSQL for history.

**Model:**
```python
class Report:
    id: str
    template_type: str
    created_at: datetime
    metrics: JSON       # Calculated metrics
    narratives: JSON    # Generated text
    data_source_id: str # Link to uploaded data
```

**Endpoints:**
```
GET /api/v1/reports              List all reports
GET /api/v1/reports/{id}         Get specific report
GET /api/v1/reports/compare      Compare two reports
```

---

## Quick Start

### If you want to test the current chat:

```bash
# Start services
docker-compose up -d

# Basic chat
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi!"}'

# Chat with data
curl -X POST "http://localhost:8000/api/v1/chat/with-data" \
  -F "message=How's my revenue?" \
  -F "file=@data/samples/revenue_sample.csv"
```

### If you want to run the tests:

```bash
# Run all service tests (no database needed)
docker-compose exec app pytest tests/services/ -v

# Run just the LLM tests
docker-compose exec app pytest tests/services/llm/ -v
```

---

## Architecture Notes

**Current flow:**
```
User Message
    ↓
Chat Endpoint (chat.py)
    ↓
Conversation Service (conversation.py)
    ↓
    ├─→ Context Builder (context_builder.py)
    │       ↓
    │   Metrics Engine (from Phase 2)
    │       ↓
    │   Formatted Context
    ↓
System Prompt + Context + History
    ↓
DeepSeek API
    ↓
Response to User
```

**For report generation, we'll add:**
```
Report Request
    ↓
Report Generator (generator.py)
    ↓
    ├─→ Template (templates.py)
    ├─→ Metrics Engine
    └─→ Narrator (for each section)
    ↓
Structured Report
    ↓
Save to PostgreSQL
    ↓
Return to User
```

---

## Success Criteria

Phase 3 is complete when:
1. Can generate a structured report from a template
2. Reports include both metrics and narratives
3. Reports are stored and retrievable
4. At least 2 template types working
5. Tests for report generation

---

## Files to Reference

- Current chat: `app/api/v1/chat.py`
- Conversation service: `app/services/llm/conversation.py`
- Context builder: `app/services/llm/context_builder.py`
- Echo persona: `app/services/llm/prompts/consultant.py`
- Original Phase 3 plan: `planning/04_PHASE_3_WORKFLOW_AND_USER_FLOW.md`

---

*Last updated: 2025-11-24*
