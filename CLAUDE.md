# CLAUDE.md - AI Assistant Guide

## Project Overview

**Project Name**: SEO & AI Visibility Analysis Tool
**Purpose**: Analyse websites for SEO health (backlinks, technical issues, content structure) and project ROI from optimisation investments
**Target Users**: Non-developers, SEO professionals, digital agencies
**Development Approach**: Staged MVP development
**Current Stage**: Stage 1 - Minimal working backend

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Runtime**: Python 3.10+
- **Server**: Uvicorn (ASGI server)

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

### Future Structure (Stages 2-3)
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
│   ├── ai_analysis.py  # AI visibility analysis (Stage 2)
│   └── roi.py          # ROI calculations
├── utils/
│   ├── __init__.py
│   └── csv_parser.py   # CSV handling utilities
├── data/
│   └── storage.db      # SQLite database (Stage 3)
└── tests/
    ├── __init__.py
    └── test_scoring.py
```

## Code Architecture

### main.py Structure

The entire application is currently in `main.py` (monolithic for MVP simplicity):

1. **Imports and App Initialisation** (lines 1-18)
   - FastAPI imports
   - Data processing libraries (pandas, numpy)
   - App instance creation

2. **Scoring Functions** (lines 20-275)
   - `score_backlinks()` - Lines 21-95
   - `score_technical()` - Lines 98-226
   - `score_content_structure()` - Lines 229-310
   - `project_roi()` - Lines 313-370

3. **API Endpoints** (lines 373-450)
   - `GET /` - Health check
   - `POST /analyse` - Main analysis endpoint

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

#### 4. ROI Projection (`project_roi()`)

**Input Parameters**:
- `backlink_score` (float 0-100)
- `technical_score` (float 0-100)
- `content_structure_score` (float 0-100)
- `monthly_traffic` (int)
- `conversion_rate` (float, percentage)
- `avg_order_value` (float, £)
- `investment_amount` (float, £)

**Weighting Formula**:
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
**Purpose**: Health check
**Response**: JSON with service status and version

### POST /analyse
**Purpose**: Main analysis endpoint
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

4. **Access API documentation**:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

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

## Future Development (Stages 2-3)

### Stage 2: AI Visibility Analysis
- **LLM Integration**: OpenAI/Anthropic API for content relevance
- **Schema.org Detection**: Structured data analysis
- **E-E-A-T Scoring**: Expertise, Experience, Authoritativeness, Trust
- **AI Search Optimisation**: ChatGPT, Perplexity, Claude visibility

**New Endpoint**: `POST /analyse-ai`

**Changes to `project_roi()`**: Replace fixed `ai_visibility_baseline` with actual score

### Stage 3: Persistence & Tracking
- **Database**: SQLite initially, PostgreSQL for production
- **Historical Data**: Track scores over time
- **Comparison Reports**: Before/after analysis
- **User Accounts**: Multi-user support
- **Scheduling**: Automated re-crawling

**New Files**:
- `database.py` - SQLAlchemy models
- `migrations/` - Alembic migrations
- `auth.py` - User authentication

### Stage 4: Frontend (Optional)
- **Framework**: React or simple HTML/CSS/JS
- **Features**:
  - File upload interface
  - Visual dashboards
  - PDF report generation
  - Historical charts

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
- Manual testing via Postman/cURL
- Sample CSV files for validation

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

### Stage 1 (Current) - 2026-01-19
- ✅ Initial project setup
- ✅ FastAPI application structure
- ✅ Backlink scoring implementation
- ✅ Technical SEO scoring implementation
- ✅ Content structure scoring implementation
- ✅ ROI projection calculation
- ✅ POST /analyse endpoint
- ✅ CSV file upload handling
- ✅ Comprehensive documentation

### Stage 2 (Planned)
- ⏳ AI visibility analysis with LLM integration
- ⏳ Schema.org detection
- ⏳ E-E-A-T scoring
- ⏳ Enhanced ROI calculations with AI visibility

### Stage 3 (Planned)
- ⏳ Database persistence (SQLite/PostgreSQL)
- ⏳ Historical tracking
- ⏳ Comparison reports
- ⏳ User accounts and authentication

---

**Last Updated**: 2026-01-19
**Current Version**: 1.0.0 - Stage 1
**Maintained By**: Discovrd Agency Development Team
