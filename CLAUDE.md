# CLAUDE.md - AI Assistant Guide

## Project Overview

**Project Name**: SEO & AI Visibility Analysis Tool
**Purpose**: Analyse websites for SEO health (backlinks, technical issues, content structure, AI visibility) and project ROI from optimisation investments
**Target Users**: Non-developers, SEO professionals, digital agencies
**Development Approach**: Staged MVP development
**Current Stage**: Stage 3 - AI Visibility Analysis (Mock Implementation)

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Runtime**: Python 3.10+
- **Server**: Uvicorn (ASGI server)

### Frontend (Stage 2)
- **HTML5**: Semantic markup
- **CSS3**: Inline styles with gradient backgrounds
- **No JavaScript**: Pure HTML forms with server-side rendering
- **Responsive**: Mobile-friendly design with CSS Grid

### Data Processing
- **pandas**: CSV file parsing and data manipulation
- **numpy**: Numerical computations

### Deployment Targets
- Local development (Python 3.10+)
- Replit
- GitHub Codespaces
- Any Python-capable hosting environment

## Project Structure

```
discovrd-support-tool/
├── main.py              # Main FastAPI application (all logic currently here)
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules for Python projects
├── README.md           # User-facing documentation
└── CLAUDE.md           # This file - AI assistant guide
```

### Future Structure (Stages 3-4)
```
discovrd-support-tool/
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── CLAUDE.md
├── api/
│   ├── __init__.py
│   ├── routes.py       # API endpoints
│   └── models.py       # Pydantic models
├── services/
│   ├── __init__.py
│   ├── scoring.py      # Scoring logic
│   ├── ai_analysis.py  # AI visibility analysis (Stage 3)
│   └── roi.py          # ROI calculations
├── templates/
│   ├── form.html       # HTML form template
│   └── report.html     # HTML report template
├── utils/
│   ├── __init__.py
│   └── csv_parser.py   # CSV handling utilities
├── data/
│   └── storage.db      # SQLite database (Stage 4)
└── tests/
    ├── __init__.py
    └── test_scoring.py
```

**Note**: Currently all HTML is inline in main.py. Future refactoring may extract templates to separate files.

## Code Architecture

### main.py Structure

The entire application is currently in `main.py` (~1413 lines, monolithic for MVP simplicity):

1. **Imports and App Initialisation** (lines 1-14)
   - FastAPI imports (including HTMLResponse)
   - Data processing libraries (pandas, numpy)
   - App instance creation

2. **AI Visibility Module (Stage 3)** (lines 17-260)
   - `LLMTester` class - Mock LLM testing abstraction (lines 23-142)
   - `score_ai_visibility()` - AI visibility scoring (lines 145-260)
   - TODO comments for real API integration

3. **Traditional Scoring Functions** (lines 263-638)
   - `score_backlinks()` - Lines 263-339
   - `score_technical()` - Lines 342-472
   - `score_content_structure()` - Lines 475-574
   - `project_roi()` - Lines 577-638 (now includes AI visibility parameter)

4. **Web Interface Endpoints** (lines 641-1407)
   - `GET /` - HTML form with AI fields (lines 641-848)
   - `POST /analyse-form` - HTML report with AI section (lines 851-1291)
   - `POST /analyse` - JSON API with AI visibility (lines 1294-1391)
   - `GET /health` - Health check JSON (lines 1394-1402)

**Stage 3 Changes**:
- Added `LLMTester` class for mock LLM testing
- Implemented `score_ai_visibility()` function
- Added brand_name, competitor_names, test_queries inputs
- Updated `project_roi()` to accept ai_visibility_score
- Added AI visibility section to HTML report
- Updated all endpoints to include AI visibility
- Added comprehensive TODO comments for real API integration

### Scoring Algorithms

#### 1. Backlink Health Score (`score_backlinks()`)

**Input**: DataFrame with columns:
- `source_url` (required)
- `source_domain` (optional)
- `domain_authority` (required)
- `link_type` (required) - "dofollow" or "nofollow"
- `spam_score` (required) - 0-100

**Logic**:
```python
health_score = (DA_score * 0.4) + (dofollow_ratio * 0.3) + (toxicity_score * 0.3)
```

**Components**:
- **DA Score (40%)**: Average domain authority of backlinks
- **Dofollow Ratio (30%)**: Percentage of dofollow links
- **Toxicity Score (30%)**: Inverse of toxic links (spam_score > 50)

**Output**: Dict with `health_score` (0-100) and detailed metrics

**Edge Cases**:
- Empty DataFrame returns score of 0
- Missing `source_domain` triggers domain extraction from URL
- Handles missing columns gracefully with defaults

#### 2. Technical Health Score (`score_technical()`)

**Input**: DataFrame from Screaming Frog CSV:
- `URL` / `Address` / `Page`
- `Status Code` / `StatusCode`
- `Title 1` / `Title`
- `Meta Description 1` / `Description`
- `Word Count` / `WordCount`

**Column Normalisation**: Handles multiple naming conventions for columns

**Logic**:
```python
# Penalties (0-100 scale)
error_penalty = (4xx_5xx_count / total) * 100 * 0.4
title_penalty = (missing_titles / total) * 100 * 0.3
thin_content_penalty = (pages_<300_words / total) * 100 * 0.2
meta_penalty = (missing_meta / total) * 50 * 0.1

health_score = 100 - total_penalty
```

**Issue Classification**:
- **Critical**: 4XX/5XX errors (affects user experience)
- **Important**: Missing titles, thin content
- **Optimisations**: Missing meta descriptions

**Output**: Dict with `health_score`, lists of issues by priority

**Edge Cases**:
- Flexible column name matching (case-insensitive, multiple variants)
- Handles non-numeric values in numeric columns
- Provides examples of affected pages (max 3 examples)

#### 3. Content Structure Score (`score_content_structure()`)

**Input**: Same DataFrame as technical scoring

**Logic**:
```python
word_count_score = (pages_500+_words / total) * 100  # 50% weight
title_score = 100 - ((long_titles + short_titles) / total) * 100  # 30% weight
consistency_score = 100 - (pages_needing_work / total) * 100  # 20% weight

structure_score = (word_count_score * 0.5) + (title_score * 0.3) + (consistency_score * 0.2)
```

**Thresholds**:
- **Title Length**: 30-65 characters optimal
- **Word Count**:
  - <300 words = thin content
  - 300-500 words = moderate
  - 500+ words = good content

**Output**: Dict with `score`, `pages_requiring_restructuring`, and `quick_wins` list

**Quick Wins Logic**:
- Identifies top 5 actionable improvements
- Provides specific counts and recommendations

#### 4. AI Visibility Score (`score_ai_visibility()`) - Stage 3

**Input Parameters**:
- `brand` (string) - Brand name to test
- `competitor_names` (string) - Comma-separated competitor names (optional)
- `test_queries` (string) - Newline-separated test queries (optional)

**Logic**:
```python
# Parse inputs
competitors = [c.strip() for c in competitor_names.split(',') if c.strip()]
queries = [q.strip() for q in test_queries.split('\n') if q.strip()] or default_queries

# Test queries using LLMTester
tester = LLMTester("MockClaude")  # TODO: Replace with real LLM APIs
result = tester.test_queries(queries, brand, competitors)

# Calculate visibility score
visibility_score = (mention_ratio * 60) + (position_score * 40)
```

**LLMTester Class**:
- Provides unified interface for testing across different LLMs
- Currently implements mock responses for MVP
- Designed to be extended with real API calls

**Mock Implementation**:
- Simulates brand mentions based on query type:
  - Brand queries: 80% visibility
  - Product/comparison queries: 40% visibility
  - General queries: 20% visibility
- Calculates position score (lower position = higher score)
- Tracks competitor mentions

**TODO - Real API Integration**:
```python
# TODO: Add real Claude API integration (Anthropic SDK)
# TODO: Add real OpenAI API integration (ChatGPT)
# TODO: Add real Gemini API integration (Google)
# TODO: Add Perplexity API integration
# TODO: Implement rate limiting and error handling
# TODO: Add caching for repeated queries
# TODO: Implement async/parallel testing across LLMs
```

**Output**: Dict with:
- `visibility_score` (float 0-100) - Overall AI visibility
- `llm_performance` (list) - Results per LLM tested
- `by_query_type` (dict) - Breakdown by query type (brand, product, comparison, recommendation)
- `recommendations` (list) - Actionable suggestions

**Edge Cases**:
- Empty test queries trigger default query generation
- Competitor names can be URLs or plain text
- Handles missing competitors gracefully

#### 5. ROI Projection (`project_roi()`)

**Input Parameters**:
- `backlink_score` (float 0-100)
- `technical_score` (float 0-100)
- `content_structure_score` (float 0-100)
- `ai_visibility_score` (float 0-100) - Added in Stage 3
- `monthly_traffic` (int)
- `conversion_rate` (float, percentage)
- `avg_order_value` (float, £)
- `investment_amount` (float, £)

**Weighting Formula** (Updated in Stage 3):
```python
overall_health = (
    backlink_score * 0.30 +
    technical_score * 0.25 +
    ai_visibility_baseline * 0.25 +  # Fixed at 30% for Stage 1
    content_structure_score * 0.20
)
```

**Traffic Uplift Model**:
- Improvement potential = (100 - overall_health) / 100
- Traffic uplift = improvement_potential * 70%  (7% per 10 points)
- Conservative estimate: 7% traffic increase per 10-point score improvement

**Revenue Calculation**:
```python
additional_traffic = monthly_traffic * (uplift_percentage / 100)
additional_conversions = additional_traffic * (conversion_rate / 100)
additional_monthly_revenue = additional_conversions * avg_order_value
annual_revenue_increase = additional_monthly_revenue * 12
roi_percent = ((annual_increase - investment) / investment) * 100
```

**Output**: Dict with traffic, revenue projections, and ROI percentage

## API Endpoints

### GET /
**Purpose**: Web interface - HTML form for analysis
**Response**: HTMLResponse with embedded CSS form
**Usage**: Open in browser for non-technical users

**Features**:
- Responsive design with gradient background
- File upload inputs for CSV files
- Input validation (required fields, file types)
- Clean, modern UI with no JavaScript required

### POST /analyse-form
**Purpose**: Process form submission and return HTML report
**Content-Type**: `multipart/form-data`
**Response**: HTMLResponse with visual report

**Features**:
- Colour-coded health scores (green/amber/red)
- Interactive score cards
- Categorised issues (Critical/Important/Optimisation)
- Printable report format
- ROI projections in visual cards
- Error handling with styled error pages

### POST /analyse
**Purpose**: JSON API for programmatic access
**Content-Type**: `multipart/form-data`

**Form Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `website_url` | string | Yes | URL of website being analysed |
| `monthly_traffic` | int | Yes | Current monthly visitors |
| `conversion_rate` | float | Yes | Conversion rate as percentage (e.g., 2.5 for 2.5%) |
| `avg_order_value` | float | Yes | Average order value in £ |
| `investment_amount` | float | Yes | Planned SEO investment in £ |
| `sf_file` | File (CSV) | Yes | Screaming Frog export |
| `backlink_file` | File (CSV) | Yes | Backlink data export |

**Response Format**:
```json
{
  "website": "string",
  "overall_health_score": "float (0-100)",
  "backlinks": {
    "health_score": "float",
    "metrics": { "..." }
  },
  "technical": {
    "health_score": "float",
    "critical_issues": ["..."],
    "important_issues": ["..."],
    "optimisations": ["..."]
  },
  "content_structure": {
    "score": "float",
    "pages_requiring_restructuring": "int",
    "quick_wins": ["..."]
  },
  "roi_projection": {
    "additional_monthly_traffic": "int",
    "additional_monthly_revenue": "float",
    "annual_revenue_increase": "float",
    "roi_percent": "float"
  }
}
```

**Error Response** (400):
```json
{
  "error": "Analysis failed",
  "detail": "error description"
}
```

### GET /health
**Purpose**: API health check (JSON)
**Response**: JSON with service status and version

```json
{
  "status": "operational",
  "service": "SEO & AI Visibility Analysis Tool",
  "version": "2.0.0 - Stage 2"
}
```

**Note**: Use `/health` for API monitoring. The root `/` endpoint now serves HTML instead of JSON.

## Development Workflow

### Local Development Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run development server**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the application**:
   - Web Interface: http://127.0.0.1:8000/
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc
   - Health Check: http://127.0.0.1:8000/health

### Testing the API

**Using Postman**:
1. Create POST request to `http://127.0.0.1:8000/analyse`
2. Body type: `form-data`
3. Add text fields: website_url, monthly_traffic, conversion_rate, avg_order_value, investment_amount
4. Add file fields: sf_file, backlink_file
5. Send request

**Using cURL**:
```bash
curl -X POST "http://127.0.0.1:8000/analyse" \
  -F "website_url=https://example.com" \
  -F "monthly_traffic=10000" \
  -F "conversion_rate=2.5" \
  -F "avg_order_value=50.00" \
  -F "investment_amount=5000.00" \
  -F "sf_file=@screaming-frog.csv" \
  -F "backlink_file=@backlinks.csv"
```

**Using FastAPI Swagger UI**:
1. Navigate to http://127.0.0.1:8000/docs
2. Expand POST /analyse
3. Click "Try it out"
4. Fill in form fields and upload files
5. Click "Execute"

### Git Workflow

**Branch Strategy**: Feature branches with `claude/` prefix

**Current Branch**: `claude/claude-md-mkl70zjah3k6lvmu-Kf7ET`

**Commit Conventions**:
- Use clear, descriptive commit messages
- UK English spelling in messages
- Format: `<type>: <description>`
  - Types: feat, fix, docs, refactor, test, chore

**Example Commits**:
```
feat: implement backlink scoring algorithm
fix: handle missing CSV columns gracefully
docs: add API usage examples to README
refactor: extract scoring functions to separate module
```

**Push Command**:
```bash
git push -u origin claude/claude-md-mkl70zjah3k6lvmu-Kf7ET
```

## Key Conventions

### Code Style

1. **UK English**: All labels, comments, variable names, and documentation
   - ✅ `analyse`, `optimisation`, `colour`
   - ❌ `analyze`, `optimization`, `color`

2. **PEP 8 Compliance**: Follow Python style guide
   - 4 spaces for indentation
   - Max line length: 100 characters (flexible for readability)
   - Snake_case for functions and variables
   - PascalCase for classes

3. **Type Hints**: Use where beneficial for clarity
   ```python
   def score_backlinks(df: pd.DataFrame) -> dict:
   ```

4. **Docstrings**: Google-style docstrings for functions
   ```python
   """
   Calculate backlink health score (0-100).

   Args:
       df: DataFrame with backlink data

   Returns:
       Dict with health_score and metrics
   """
   ```

### Error Handling

1. **Graceful Degradation**: Return sensible defaults for missing data
2. **User-Friendly Messages**: Clear error descriptions in API responses
3. **No Stack Traces to Users**: Catch exceptions and return 400/500 with details

### Data Validation

1. **CSV Column Flexibility**: Support multiple naming conventions
2. **Type Coercion**: Convert strings to numbers with `pd.to_numeric(errors='coerce')`
3. **Empty Data Handling**: Always check for empty DataFrames

## Future Development (Stages 3-4)

### Stage 2: Web UI ✅ COMPLETE
- **HTML Forms**: Clean, responsive web interface
- **Visual Reports**: Colour-coded scores and issue categorisation
- **No JavaScript**: Pure server-side rendering
- **Print Support**: Printable HTML reports

**Completed Features**:
- GET / endpoint serves HTML form
- POST /analyse-form returns HTML report
- Inline CSS with gradient design
- Mobile-responsive layout

### Stage 3: AI Visibility Analysis ✅ COMPLETE (Mock)
- **LLMTester Class**: Unified interface for LLM testing
- **Mock Implementation**: Query-based visibility testing
- **Query Types**: Brand, product, comparison, recommendation breakdown
- **Competitor Tracking**: Monitor competitor mentions
- **Recommendations Engine**: Automated improvement suggestions
- **ROI Integration**: AI visibility now part of overall health score

**Completed Features**:
- LLMTester class with comprehensive TODO comments
- score_ai_visibility() function
- Form inputs for brand, competitors, and test queries
- AI visibility section in HTML reports
- Mock scoring based on query characteristics
- Ready for real API integration

**TODO for Stage 4**:
- Replace mock with real Claude API (Anthropic SDK)
- Add real ChatGPT API (OpenAI SDK)
- Add real Gemini API (Google SDK)
- Add Perplexity API
- Implement async/parallel testing
- Add rate limiting and caching

### Stage 4: Real LLM Integration (Planned)
- **Real API Calls**: Replace mock with actual LLM APIs
- **Claude API**: Anthropic SDK integration
- **ChatGPT API**: OpenAI SDK integration
- **Gemini API**: Google SDK integration
- **Perplexity API**: Direct API integration
- **Parallel Testing**: Async testing across multiple LLMs
- **Rate Limiting**: Respect API rate limits
- **Caching**: Cache query results to reduce API costs
- **Error Handling**: Graceful fallbacks for API failures
- **Schema.org Detection**: Structured data analysis
- **E-E-A-T Scoring**: Content quality metrics

**New Dependencies**:
- `anthropic` - Claude API SDK
- `openai` - ChatGPT API SDK
- `google-generativeai` - Gemini API SDK
- `aiohttp` - Async HTTP for parallel requests

### Stage 5: Persistence & Tracking (Planned)
- **Database**: SQLite initially, PostgreSQL for production
- **Historical Data**: Track scores over time
- **Comparison Reports**: Before/after analysis
- **User Accounts**: Multi-user support
- **Scheduling**: Automated re-crawling

**New Files**:
- `database.py` - SQLAlchemy models
- `migrations/` - Alembic migrations
- `auth.py` - User authentication
- `templates/` - Extracted HTML templates (Jinja2)

## Common Issues & Solutions

### Issue: "Module not found" errors
**Solution**: Activate virtual environment and reinstall dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: CSV parsing fails
**Cause**: Missing or misnamed columns
**Solution**: Check column names in CSV, update `score_*()` functions to handle variants

### Issue: Memory errors with large CSVs
**Solution**: Implement chunked reading with `pd.read_csv(chunksize=1000)`

### Issue: Slow processing
**Solution**:
- Add caching for repeated analyses
- Implement async processing for large files
- Add progress indicators

## Testing Strategy

### Current Testing
- **Web Interface**: Manual testing via browser at http://127.0.0.1:8000/
- **API Testing**: Postman/cURL for JSON endpoints
- **Sample Files**: CSV files for validation
- **Visual Inspection**: HTML report rendering and styling

### Future Testing (Stage 2+)
- **Unit Tests**: pytest for individual functions
- **Integration Tests**: Test full /analyse endpoint
- **Load Tests**: locust for performance testing
- **Validation Tests**: Known good/bad CSVs for regression

**Test Files Structure**:
```python
# tests/test_scoring.py
import pytest
from main import score_backlinks, score_technical

def test_backlinks_empty_df():
    df = pd.DataFrame()
    result = score_backlinks(df)
    assert result['health_score'] == 0

def test_backlinks_high_quality():
    df = pd.DataFrame({
        'source_url': ['https://quality.com/page'],
        'domain_authority': [80],
        'link_type': ['dofollow'],
        'spam_score': [5]
    })
    result = score_backlinks(df)
    assert result['health_score'] > 80
```

## Performance Considerations

### Current Performance
- **CSV Upload Limit**: 1MB default (FastAPI)
- **Processing Time**: <2 seconds for typical files (500 rows)
- **Memory Usage**: ~50MB for 1000-row CSVs

### Optimisation Opportunities
1. **Vectorisation**: Use pandas vectorised operations (already implemented)
2. **Lazy Loading**: Process files in chunks for large datasets
3. **Caching**: Cache parsed CSVs for repeated analyses
4. **Async Processing**: Background tasks for long-running analyses

## Security Considerations

### Current Implementation
- **File Upload Validation**: Only CSV files accepted
- **No Persistence**: Files not stored permanently
- **Input Sanitisation**: Pandas handles CSV parsing safely

### Future Security (Stage 2+)
- **Rate Limiting**: Prevent API abuse
- **Authentication**: JWT tokens for user accounts
- **File Size Limits**: Enforce maximum upload size
- **CSV Injection Prevention**: Sanitise CSV content
- **HTTPS Only**: Enforce encrypted connections

## Environment Variables (Future)

```bash
# .env file (Stage 2+)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@localhost/discovrd
SECRET_KEY=your-secret-key-here
DEBUG=False
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## Monitoring & Logging (Future)

### Logging Strategy
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Analysis started for %s", website_url)
```

### Metrics to Track
- Request count and response times
- Error rates by endpoint
- File upload sizes and processing times
- Score distributions

## AI Assistant Guidelines

### When Modifying Code

1. **Maintain Backward Compatibility**: Don't break existing API contracts
2. **Update Documentation**: Keep README.md and CLAUDE.md in sync
3. **Test Changes**: Verify with sample CSVs before committing
4. **Follow Conventions**: UK English, PEP 8, existing patterns

### When Adding Features

1. **Stage-Appropriate**: Consider current MVP stage
2. **Keep It Simple**: Avoid over-engineering
3. **Document Thoroughly**: Update all relevant docs
4. **Consider Future Refactoring**: Comment where code will move later

### When Debugging

1. **Check CSV Format**: Most issues stem from unexpected CSV structure
2. **Verify Column Names**: Case-sensitive matching issues
3. **Inspect DataFrames**: Use `df.head()`, `df.columns`, `df.dtypes`
4. **Review Logs**: Check console output for pandas warnings

### Common Tasks

**Add New Scoring Metric**:
1. Update relevant `score_*()` function
2. Adjust weighting in scoring formula
3. Update return dict structure
4. Document in CLAUDE.md and README.md
5. Test with sample data

**Change ROI Calculation**:
1. Modify `project_roi()` function
2. Update documentation with new formula
3. Adjust weightings if needed
4. Test with various input combinations

**Add New Endpoint**:
1. Define function with `@app.post()` decorator
2. Add request/response models (optional but recommended)
3. Implement logic
4. Update README.md with usage examples
5. Test via Swagger UI

## Resources

### External Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **pandas**: https://pandas.pydata.org/docs/
- **Uvicorn**: https://www.uvicorn.org/

### SEO Resources
- **Screaming Frog**: https://www.screamingfrog.co.uk/seo-spider/
- **SERanking**: https://seranking.com/
- **Google Search Console**: https://search.google.com/search-console

### Project Context
- **Brief**: SEO & AI Visibility Analysis Tool MVP
- **Target Audience**: Non-developers, SEO professionals
- **Deployment**: Replit, Codespaces, or local Python environment

## Changelog

### Stage 1 (Complete) - 2026-01-19
- ✅ Initial project setup
- ✅ FastAPI application structure
- ✅ Backlink scoring implementation
- ✅ Technical SEO scoring implementation
- ✅ Content structure scoring implementation
- ✅ ROI projection calculation
- ✅ POST /analyse endpoint (JSON)
- ✅ CSV file upload handling
- ✅ Comprehensive documentation

### Stage 2 (Complete) - 2026-01-19
- ✅ HTML web interface with form
- ✅ GET / endpoint serves web UI
- ✅ POST /analyse-form endpoint with HTML reports
- ✅ Responsive design with inline CSS
- ✅ Colour-coded health scores
- ✅ Visual issue categorisation
- ✅ Printable HTML reports
- ✅ GET /health endpoint for API monitoring
- ✅ Updated documentation for web interface

### Stage 3 (Current) - 2026-01-19
- ✅ LLMTester class with mock implementation
- ✅ score_ai_visibility() function
- ✅ Brand name, competitor, and custom query inputs
- ✅ Mock AI visibility scoring with query type breakdown
- ✅ AI visibility section in HTML reports
- ✅ Updated project_roi() to include AI visibility
- ✅ Comprehensive TODO comments for real API integration
- ✅ AI visibility included in JSON API responses

### Stage 4 (Planned)
- ⏳ Real LLM API integration (Claude, ChatGPT, Gemini, Perplexity)
- ⏳ Parallel testing across multiple LLMs
- ⏳ Rate limiting and caching
- ⏳ Schema.org detection
- ⏳ E-E-A-T scoring

### Stage 5 (Planned)
- ⏳ Database persistence (SQLite/PostgreSQL)
- ⏳ Historical tracking
- ⏳ Comparison reports
- ⏳ User accounts and authentication
- ⏳ Template extraction (Jinja2)

---

**Last Updated**: 2026-01-19
**Current Version**: 3.0.0 - Stage 3
**Maintained By**: Discovrd Agency Development Team
