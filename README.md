# SEO & AI Visibility Analysis Tool - Stage 1

A FastAPI-based backend service for analysing SEO health, backlinks, technical issues, and projecting ROI for optimisation investments.

## Features

- **Backlink Analysis**: Evaluates domain authority, dofollow ratio, and toxic link identification
- **Technical SEO Audit**: Identifies 4XX/5XX errors, missing meta data, and thin content
- **Content Structure Scoring**: Analyses word count distribution and title optimisation
- **ROI Projections**: Calculates potential revenue increases based on SEO improvements

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

The API will be available at: `http://127.0.0.1:8000`

- **API Documentation**: http://127.0.0.1:8000/docs (interactive Swagger UI)
- **Alternative docs**: http://127.0.0.1:8000/redoc

## API Usage

### Endpoint: `POST /analyse`

Accepts form data with CSV file uploads for analysis.

#### Required Form Fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `website_url` | string | Website being analysed | `https://example.com` |
| `monthly_traffic` | integer | Current monthly visitors | `10000` |
| `conversion_rate` | float | Conversion rate (%) | `2.5` |
| `avg_order_value` | float | Average order value (£) | `50.00` |
| `investment_amount` | float | SEO investment budget (£) | `5000.00` |

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
├── main.py              # FastAPI application with all logic
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

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

## Next Steps

**Stage 2** (Planned):
- Add AI visibility scoring using LLM APIs
- Schema.org markup detection
- Content relevance analysis

**Stage 3** (Planned):
- Persistent storage (SQLite/PostgreSQL)
- Historical tracking
- Comparison reports

## Licence

Proprietary - Discovrd Agency

## Support

For issues or questions, contact the development team.
