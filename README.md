# SEO & AI Visibility Analysis Tool - Stage 3

A FastAPI-based service with web UI for analysing SEO health, backlinks, technical issues, AI visibility, and projecting ROI for optimisation investments.

## Features

- **🎨 Web Interface**: Simple, clean form for non-technical users
- **Backlink Analysis**: Evaluates domain authority, dofollow ratio, and toxic link identification
- **Technical SEO Audit**: Identifies 4XX/5XX errors, missing meta data, and thin content
- **Content Structure Scoring**: Analyses word count distribution and title optimisation
- **🤖 AI Visibility Analysis**: Tests brand visibility across LLMs with query-based testing (Stage 3)
- **ROI Projections**: Calculates potential revenue increases including AI visibility impact
- **HTML Reports**: Beautiful, printable reports with visual score indicators
- **API Access**: Programmatic access via JSON API for integrations

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Installation

### Local Setup

1. **Clone or navigate to the repository:**
   ```bash
   cd discovrd-support-tool
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Replit / Codespaces Setup

1. Upload or clone the repository
2. Run:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application will be available at: `http://127.0.0.1:8000`

### 🌐 Web Interface (Recommended for non-technical users)

Open your browser and navigate to:
- **Web Form**: http://127.0.0.1:8000/

The web form provides:
- Simple file upload interface
- Visual HTML reports with colour-coded scores
- Printable results
- No technical knowledge required

### 🔧 API Endpoints (For developers and integrations)

- **API Documentation**: http://127.0.0.1:8000/docs (interactive Swagger UI)
- **Alternative docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health (JSON status)

## Using the Web Interface

### Step 1: Access the Form

1. Start the server with `uvicorn main:app --reload`
2. Open your browser and navigate to http://127.0.0.1:8000/
3. You'll see a clean, simple form

### Step 2: Complete the Form

Fill in the following information:

1. **Website URL**: The website you want to analyse (e.g., https://example.com)
2. **Monthly Traffic**: Current number of monthly visitors
3. **Conversion Rate**: Your current conversion rate as a percentage (e.g., 2.5 for 2.5%)
4. **Average Order Value**: Average transaction value in pounds (£)
5. **Investment Amount**: How much you plan to invest in SEO (£)

### Step 3: Complete AI Visibility Fields (Stage 3)

Fill in the AI visibility analysis fields:

1. **Brand Name**: Your company or brand name (required)
2. **Competitor Names/URLs**: Comma-separated list of competitors (optional)
3. **Custom Test Queries**: One query per line to test AI visibility (optional)
   - If not provided, default queries will be generated based on your brand

### Step 4: Upload CSV Files

Upload two CSV files:

1. **Screaming Frog CSV Export**
   - Run a crawl in Screaming Frog SEO Spider
   - Export the results as CSV
   - Ensure it contains: URL, Status Code, Title 1, Meta Description 1, Word Count

2. **Backlink CSV File**
   - Export from your backlink tool (SERanking, Ahrefs, Moz, etc.)
   - Must contain: source_url, domain_authority, link_type, spam_score
   - Can optionally include: source_domain

### Step 5: Analyse

Click the "Analyse Website" button. The tool will:
- Process both CSV files
- Calculate health scores
- Identify issues and opportunities
- Project potential ROI

### Step 6: Review Report

You'll receive a visual HTML report showing:

- **Overall Health Score**: Weighted score from all categories (including AI visibility)
- **Backlink Health**: Domain authority, dofollow ratio, toxic links
- **Technical Health**: Error pages, missing metadata, thin content
- **Content Structure**: Word count analysis, title optimisation
- **AI Visibility**: LLM performance, query type breakdown, and recommendations (Stage 3)
- **ROI Projection**: Estimated traffic and revenue increases based on all factors

The report is printable and can be saved as PDF using your browser's print function.

## API Usage

### Available Endpoints

The API provides two endpoints for analysis:

1. **`POST /analyse`** - Returns JSON response (for API integrations)
2. **`POST /analyse-form`** - Returns HTML report (used by web interface)

Both endpoints accept the same parameters and files. Use `/analyse` for programmatic access and `/analyse-form` for web-based usage.

### Endpoint: `POST /analyse`

Accepts form data with CSV file uploads for analysis and returns JSON.

#### Required Form Fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `website_url` | string | Website being analysed | `https://example.com` |
| `monthly_traffic` | integer | Current monthly visitors | `10000` |
| `conversion_rate` | float | Conversion rate (%) | `2.5` |
| `avg_order_value` | float | Average order value (£) | `50.00` |
| `investment_amount` | float | SEO investment budget (£) | `5000.00` |
| `brand_name` | string | Brand/company name | `Acme Corp` |
| `competitor_names` | string | Comma-separated competitors (optional) | `CompA, CompB` |
| `test_queries` | string | Newline-separated test queries (optional) | `best tools\ntop software` |

#### Required Files:

1. **`sf_file`** - Screaming Frog CSV Export
   - Must contain columns: `URL`, `Status Code`, `Title 1`, `Meta Description 1`, `Word Count`
   - Export from Screaming Frog crawl

2. **`backlink_file`** - Backlink CSV
   - Must contain columns: `source_url`, `domain_authority`, `link_type`, `spam_score`
   - Optional: `source_domain`
   - Export from SERanking or similar tool

## Testing with Postman

1. **Open Postman** and create a new POST request

2. **Set URL**: `http://127.0.0.1:8000/analyse`

3. **Set Body Type**:
   - Select **Body** tab
   - Choose **form-data**

4. **Add Form Fields**:
   | Key | Type | Value |
   |-----|------|-------|
   | `website_url` | Text | `https://example.com` |
   | `monthly_traffic` | Text | `10000` |
   | `conversion_rate` | Text | `2.5` |
   | `avg_order_value` | Text | `50.00` |
   | `investment_amount` | Text | `5000.00` |
   | `sf_file` | File | [Select your Screaming Frog CSV] |
   | `backlink_file` | File | [Select your backlink CSV] |

5. **Send Request** - You'll receive a JSON response with analysis results

## Testing with cURL

```bash
curl -X POST "http://127.0.0.1:8000/analyse" \
  -F "website_url=https://example.com" \
  -F "monthly_traffic=10000" \
  -F "conversion_rate=2.5" \
  -F "avg_order_value=50.00" \
  -F "investment_amount=5000.00" \
  -F "sf_file=@path/to/screaming-frog-export.csv" \
  -F "backlink_file=@path/to/backlinks.csv"
```

## Sample Response

```json
{
  "website": "https://example.com",
  "overall_health_score": 67.3,
  "backlinks": {
    "health_score": 72.0,
    "metrics": {
      "total_backlinks": 1234,
      "referring_domains": 345,
      "average_da": 41.2,
      "dofollow_ratio": 76.5,
      "toxic_links": 12
    }
  },
  "technical": {
    "health_score": 58.0,
    "critical_issues": [
      {
        "issue": "15 pages with 4XX/5XX errors",
        "priority": "Critical",
        "affected_pages": 5,
        "examples": ["https://example.com/broken-page", "..."]
      }
    ],
    "important_issues": [
      {
        "issue": "42 pages missing title tags",
        "priority": "Important",
        "affected_pages": 5,
        "examples": ["https://example.com/no-title", "..."]
      }
    ],
    "optimisations": [
      {
        "issue": "89 pages missing meta descriptions",
        "priority": "Optimisation",
        "affected_pages": 89
      }
    ]
  },
  "content_structure": {
    "score": 63.0,
    "pages_requiring_restructuring": 42,
    "quick_wins": [
      "Shorten 23 titles over 65 characters for better SERP display.",
      "Expand 42 thin pages to at least 300 words."
    ]
  },
  "ai_visibility": {
    "visibility_score": 41.0,
    "llm_performance": [
      {
        "name": "MockClaude",
        "score": 41.0,
        "citations": 4,
        "queries_tested": 10
      }
    ],
    "by_query_type": {
      "brand": 0.8,
      "product": 0.3,
      "comparison": 0.2,
      "recommendation": 0.1
    },
    "recommendations": [
      "Your brand has moderate AI visibility. Focus on creating authoritative content.",
      "Improve comparison visibility: Publish comparison guides and competitive analysis."
    ]
  },
  "roi_projection": {
    "additional_monthly_traffic": 1500,
    "additional_monthly_revenue": 1875.0,
    "annual_revenue_increase": 22500.0,
    "roi_percent": 350.0
  }
}
```

## CSV File Format Examples

### Screaming Frog Export (sf_file)

```csv
URL,Status Code,Title 1,Meta Description 1,Word Count
https://example.com/,200,Homepage Title,This is the homepage,1200
https://example.com/about,200,About Us,Learn about our company,450
https://example.com/broken,404,,,0
```

### Backlink CSV (backlink_file)

```csv
source_url,source_domain,domain_authority,link_type,spam_score
https://quality-site.com/article,quality-site.com,65,dofollow,5
https://another-site.com/blog,another-site.com,45,nofollow,15
https://spammy-site.com/link,spammy-site.com,12,dofollow,85
```

## Scoring Methodology

### Backlink Health Score (0-100)
- **Domain Authority** (40%): Average DA of referring domains
- **Dofollow Ratio** (30%): Percentage of dofollow links
- **Toxicity** (30%): Inverse of spam score percentage

### Technical Health Score (0-100)
- **4XX/5XX Errors** (40%): Critical site errors
- **Missing Titles** (30%): Pages without title tags
- **Thin Content** (20%): Pages with <300 words
- **Missing Meta Descriptions** (10%): Optimisation opportunity

### Content Structure Score (0-100)
- **Word Count** (50%): Percentage of pages with 500+ words
- **Title Optimisation** (30%): Titles within 30-65 characters
- **Content Consistency** (20%): Overall content quality distribution

### ROI Calculation
- **Overall Health**: Weighted average of all scores
  - Backlinks: 30%
  - Technical: 25%
  - AI Visibility: 25% (baseline for MVP)
  - Content Structure: 20%
- **Traffic Uplift**: ~7% increase per 10 points of improvement potential
- **Revenue Impact**: Additional traffic × conversion rate × average order value
- **ROI**: (Annual revenue increase - investment) / investment × 100

## Project Structure

```
discovrd-support-tool/
├── main.py              # FastAPI application with web UI and API endpoints
├── requirements.txt     # Python dependencies
├── README.md           # This file (user documentation)
├── CLAUDE.md           # AI assistant guide
└── .gitignore          # Git ignore patterns
```

All logic is currently in `main.py` for simplicity. Future stages may refactor into modules.

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **CSV parsing errors**
   - Verify CSV files have required columns
   - Check for proper CSV formatting (no extra commas, proper encoding)

3. **Port already in use**
   - Change port: `uvicorn main:app --reload --port 8001`

4. **File upload size limits**
   - Default FastAPI limit is 1MB for file uploads
   - For larger files, configure `max_upload_size` in FastAPI

## Development Roadmap

**Stage 1** (✅ Complete):
- FastAPI backend with scoring algorithms
- JSON API endpoints
- CSV file processing

**Stage 2** (✅ Complete):
- Web interface with HTML form
- Visual HTML reports with colour-coded scores
- Improved user experience for non-technical users

**Stage 3** (✅ Complete):
- AI visibility scoring with mock LLM testing (ready for real API integration)
- Query-based testing across different query types
- Brand vs competitor visibility comparison
- AI visibility recommendations
- Integrated into ROI calculations

**Stage 4** (Planned):
- Real LLM API integration (Claude, ChatGPT, Gemini, Perplexity)
- Schema.org markup detection
- Content relevance analysis
- E-E-A-T evaluation

**Stage 5** (Planned):
- Persistent storage (SQLite/PostgreSQL)
- Historical tracking
- Comparison reports
- User accounts and authentication

## Licence

Proprietary - Discovrd Agency

## Support

For issues or questions, contact the development team.
