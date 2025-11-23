# Echo - AI Data Scientist for Small Businesses

> Building an AI-powered analytics tool that turns messy business data into clear insights. Because small businesses deserve good data tools too.

**Status**: In Development - Phase 2 Complete
**Powered by**: DeepSeek 3.2, FastAPI, PostgreSQL, Redis
**Goal**: Transform 2-hour manual reports into 15-minute automated insights

---

## What I'm Building

Most small businesses drown in spreadsheets but can't afford a full-time data analyst. Echo is my solution to that problem.

**The core idea**:
- Upload your business data (Stripe exports, HubSpot CSVs, whatever you've got)
- Get accurate metrics calculated automatically (no LLM hallucinations on the math)
- Receive plain-English explanations powered by AI
- Ask follow-up questions in natural language

**Why "deterministic metrics + LLM narrative"?**
I don't trust LLMs to do calculations. They're great at explaining things, terrible at math. So I'm building it the right way:
- Calculate metrics using SQL/Python (accurate, testable)
- Use LLM (DeepSeek) only for explanations and insights
- No made-up numbers, just facts with context

---

## Current Status

### Phase 2 Complete (Deterministic Analytics)
The metrics engine is done. 20 business metrics, all deterministic math, no AI hallucinations.

**What's working:**
- 7 revenue metrics (Total Revenue, MRR, ARR, Growth Rate, AOV, Revenue by Period/Product)
- 6 financial metrics (CAC, LTV, LTV:CAC Ratio, Gross Margin, Burn Rate, Runway)
- 7 marketing metrics (Conversion Rate, Channel/Campaign Performance, CPL, ROAS, Lead Velocity, Funnel)
- Time-series analysis (trends, growth, period comparisons)
- 124 tests passing, 88% coverage

Try it:
```bash
# Start the services
docker-compose up -d

# Calculate revenue metrics from a CSV
curl -X POST "http://localhost:8000/api/v1/metrics/calculate/revenue" \
  -F "file=@data/samples/revenue_sample.csv"
```

Example output (real numbers from sample data):
```
total_revenue: $190,100.50
  transaction_count: 92
  average_transaction: $2,066.31

revenue_by_period:
  2024-01: $51,930.50
  2024-02: $54,900.00
  2024-03: $61,190.00
  2024-04: $22,080.00

revenue_by_product:
  Enterprise: $124,720.50 (38 transactions, avg $3,282.12)
  Pro Plan: $57,330.00 (41 transactions, avg $1,398.29)
  Basic: $8,050.00 (13 transactions, avg $619.23)

mrr: $190,100.50
arr: $2,281,206.00
revenue_growth: -63.92% (Apr vs Mar - expected, Apr data is partial)
```

Marketing metrics output:
```
conversion_rate: 10.21%
  total_leads: 17,254
  total_conversions: 1,762

channel_performance:
  Facebook: 6,482 leads, 649 conversions, 10.01% rate, $24.47 CPC
  Google Ads: 5,933 leads, 642 conversions, 10.82% rate, $26.93 CPC
  Email: 3,168 leads, 288 conversions, 9.09% rate, $1.74 CPC
  LinkedIn: 848 leads, 148 conversions, 17.45% rate, $32.43 CPC
  Twitter: 823 leads, 35 conversions, 4.25% rate, $49.14 CPC

cost_per_lead: $2.33
top_channel: Facebook (by volume)
best_conversion: LinkedIn (17.45%)
cheapest_acquisition: Email ($1.74 per conversion)
```

All numbers verified against manual calculations. Pure pandas math, no AI involved.

### Next Up: Phase 3 (LLM Intelligence)
What I'm building next:
- Report templates (Weekly Revenue, Marketing Funnel)
- DeepSeek narrative generation from these metrics
- Natural language Q&A about the data

---

## API Endpoints

### Health
```
GET  /                        Service info
GET  /api/v1/health           Basic health check
GET  /api/v1/health/db        Database health
GET  /api/v1/health/redis     Redis health
```

### Ingestion (Phase 1)
```
POST /api/v1/ingestion/upload/csv     Upload CSV file
POST /api/v1/ingestion/upload/excel   Upload Excel file
GET  /api/v1/ingestion/sources        List all uploaded sources
GET  /api/v1/ingestion/sources/{id}   Get source by ID
```

### Metrics (Phase 2)
```
GET  /api/v1/metrics/available           List all available metrics
POST /api/v1/metrics/calculate/csv       Calculate any metrics from CSV
POST /api/v1/metrics/calculate/revenue   Revenue metrics only
POST /api/v1/metrics/calculate/marketing Marketing metrics only
POST /api/v1/metrics/trend               Trend analysis on a column
POST /api/v1/metrics/growth              Growth analysis over time
```

### API Documentation
```
GET  /api/v1/docs             Swagger UI
GET  /api/v1/redoc            ReDoc
```

---

## The Plan (5-6 Weeks)

I'm building this in 6 phases:

**Phase 0** - Foundation (Complete)
Docker environment, FastAPI + PostgreSQL + Redis, health checks

**Phase 1** - Data Ingestion (Complete)
File upload, schema detection, data validation, storage

**Phase 2** - Analytics Engine (Complete)
20 metrics: MRR, ARR, CAC, LTV, conversion rates, channel performance, funnel analysis

**Phase 3** - Intelligence (Next)
LLM-powered insights, natural language Q&A

**Phase 4** - Evaluation
Time tracking, accuracy metrics, user feedback

**Phase 5** - Production Ready
Tests, CI/CD, monitoring, error handling

**Phase 6** - Polish
Documentation, demos, portfolio presentation

Full roadmap: See `/planning/` folder

---

## Tech Stack

**Why I chose these tools:**

- **FastAPI** - Fast, modern, auto-generates docs
- **PostgreSQL** - Reliable, handles complex queries
- **Redis** - Cache repeated calculations
- **DeepSeek** - Affordable, powerful LLM (OpenAI-compatible API)
- **Docker** - Consistent dev environment
- **Pandas** - Data processing workhorse

**Full stack:**
```
Backend:     FastAPI, Python 3.11
Database:    PostgreSQL 15 (async)
Cache:       Redis 7
AI/LLM:      DeepSeek 3.2
Testing:     pytest, pytest-cov (88% coverage)
Monitoring:  structlog, Prometheus
DevOps:      Docker, GitHub Actions
```

---

## How to Run This

### Prerequisites
- Docker & Docker Compose
- DeepSeek API key (or OpenAI key)



### Development Commands
```bash
# View logs
docker-compose logs app -f

# Run tests
docker-compose exec app pytest

# Run tests with coverage
docker-compose exec app pytest --cov=app

# Restart after code changes
docker-compose restart app

# Stop everything
docker-compose down
```

---

## Project Structure

```
Echo/
├── app/                    # Main application
│   ├── api/v1/            # API endpoints
│   │   ├── health.py      # Health checks
│   │   ├── ingestion.py   # File upload endpoints
│   │   └── metrics.py     # Metrics calculation endpoints
│   ├── core/              # Database, cache, config
│   ├── models/            # SQLAlchemy & Pydantic models
│   │   ├── data_source.py # Upload tracking model
│   │   └── schemas.py     # API schemas
│   └── services/          # Business logic
│       ├── schema_detector.py   # Auto-detect column types
│       ├── data_validator.py    # Validation engine
│       ├── ingestion.py         # Upload orchestration
│       ├── metrics/             # Deterministic analytics (Phase 2)
│       │   ├── base.py          # BaseMetric, MetricResult
│       │   ├── engine.py        # MetricsEngine orchestrator
│       │   ├── registry.py      # Metric discovery
│       │   ├── revenue.py       # 7 revenue metrics
│       │   ├── financial.py     # 6 financial metrics
│       │   ├── marketing.py     # 7 marketing metrics
│       │   └── timeseries.py    # Time-series utilities
│       └── llm/                 # DeepSeek integration (Phase 3)
├── tests/                 # Test suite (124 tests)
│   ├── api/              # API tests
│   └── services/         # Service tests
│       └── metrics/      # Metrics tests (75 tests)
├── planning/              # Detailed phase docs
├── data/samples/          # Sample datasets
│   ├── revenue_sample.csv
│   ├── marketing_sample.csv
│   └── bad_data_sample.csv
├── docker-compose.yml     # Services orchestration
└── requirements.txt       # Python dependencies
```

---

## What Makes This Different

**Not another analytics dashboard**
This isn't trying to be Tableau. It's focused on answering specific questions SMB owners actually ask:
- "How much did we make this month?"
- "Which marketing channel is working?"
- "Are we spending too much to acquire customers?"

**Deterministic + AI hybrid**
Most "AI analytics" tools just throw everything at an LLM and hope. I'm being deliberate:
- Hard calculations in code (testable, accurate)
- LLM for explanation (context, recommendations)
- Best of both worlds

**Built for real businesses**
Every feature is designed around actual SMB needs:
- Works with messy data (helpful error messages)
- Connects to tools they already use (Stripe, HubSpot)
- Plain English, no jargon

---

## Metrics I'm Tracking

To prove this actually works, I'm measuring:

**Time saved**
Target: 2 hours manual -> 15 minutes automated (8x faster)

**User satisfaction**
Target: >4.0/5 rating on generated insights

**Accuracy**
Target: >90% match with expert analysis (using golden datasets)

**Code Quality**
Current: 88% test coverage, 124 passing tests

---

## Current Roadmap

### Phase 0: Foundation (Complete)
- [x] Docker environment
- [x] FastAPI + PostgreSQL + Redis
- [x] Health checks working
- [x] DeepSeek configured

### Phase 1: Ingestion (Complete)
- [x] CSV/Excel upload
- [x] Schema detection (date, currency, email, URL, boolean)
- [x] Data validation with helpful messages
- [x] Store uploads in PostgreSQL
- [x] 39 tests, 88% coverage

### Phase 2: Analytics (Complete)
- [x] Revenue metrics (Total, MRR, ARR, Growth, AOV, by Period, by Product)
- [x] Financial metrics (CAC, LTV, LTV:CAC, Gross Margin, Burn Rate, Runway)
- [x] Marketing metrics (Conversion, Channel, Campaign, CPL, ROAS, Velocity, Funnel)
- [x] Time-series utilities (trends, growth, comparisons)
- [x] Metrics API endpoints
- [x] 124 tests, 88% coverage

### Phase 3: Intelligence (Next)
- [ ] Report templates
- [ ] DeepSeek narrative generation
- [ ] Natural language Q&A

See `/planning/` for detailed plans.

---

## Development Log

**2025-11-23** - Phase 2 Complete
Built the entire deterministic analytics layer:
- 20 business metrics across revenue, financial, and marketing categories
- Time-series analysis with trend detection and growth calculations
- 6 new API endpoints for metric calculation
- All metrics verified against manual calculations - pure pandas math, no AI
- 124 tests passing with 88% coverage

Key metrics working:
- Revenue: $190,100.50 total from sample data (verified)
- Marketing: 10.21% conversion rate across 17,254 leads (verified)
- Channel analysis: Email cheapest at $1.74/conversion, LinkedIn best rate at 17.45%

Files created: 8 new service files, 5 test files, 1 API endpoint file
Ready for Phase 3: LLM narrative generation

**2025-11-22** - Phase 1 Complete
Built the entire data ingestion layer:
- Schema detector that auto-identifies column types (date, currency, email, URL, boolean)
- Validation engine with helpful error messages
- CSV and Excel upload endpoints
- All metadata stored in PostgreSQL
- 39 tests passing with 88% coverage

Files created: 12 new files, 7 modified
Ready for Phase 2: Analytics Engine

**2025-11-19** - Phase 0 Complete
Got the entire foundation working. FastAPI running, Docker containers healthy, all health checks passing. DeepSeek API key configured.

---

## Why I'm Building This

Small businesses are the backbone of the economy, but they're stuck with either:
1. Manual spreadsheet hell (hours of work, error-prone)
2. Enterprise tools they can't afford ($500+/month, too complex)

There's a gap for something simple, affordable, and actually useful. That's what Echo is.

Plus, this is a great way to showcase:
- Data engineering (pipelines, validation, ETL)
- Backend development (APIs, databases, caching)
- AI/ML application (practical LLM use, not just prompting)
- Product thinking (real user needs, measurable value)

---

## Want to Follow Along?

- Check `/planning/` for detailed phase documentation
- See `PHASE_2_COMPLETE.md` for the latest completed work
- Read `WHATS_NEXT.md` for immediate next steps

---

## License

MIT - Build whatever you want with this

---

## Contact

Building in public. Questions? Feedback? Open an issue.

---

*Last updated: 2025-11-23*
*Current phase: Phase 3 - LLM Intelligence*
*LLM: DeepSeek 3.2*
