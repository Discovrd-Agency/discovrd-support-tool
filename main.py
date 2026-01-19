"""
SEO & AI Visibility Analysis Tool - Stage 2
FastAPI backend with web UI for analysing backlinks, technical SEO, and content structure
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import pandas as pd
import numpy as np
import io
from decimal import Decimal

app = FastAPI(title="SEO & AI Visibility Analysis Tool")


def score_backlinks(df: pd.DataFrame) -> dict:
    """
    Calculate backlink health score (0-100) based on:
    - Average Domain Authority (DA)
    - Dofollow ratio
    - Toxic/spam links

    Expected columns: source_url, source_domain (optional), domain_authority, link_type, spam_score
    """

    if df.empty:
        return {
            "health_score": 0,
            "metrics": {
                "total_backlinks": 0,
                "referring_domains": 0,
                "average_da": 0.0,
                "dofollow_ratio": 0.0,
                "toxic_links": 0
            }
        }

    # Calculate metrics
    total_backlinks = len(df)

    # Count referring domains (use source_domain if available, otherwise extract from source_url)
    if 'source_domain' in df.columns:
        referring_domains = df['source_domain'].nunique()
    else:
        # Simple domain extraction from URLs
        referring_domains = df['source_url'].apply(
            lambda x: x.split('/')[2] if isinstance(x, str) and '://' in x else x
        ).nunique()

    # Average DA
    if 'domain_authority' in df.columns:
        average_da = df['domain_authority'].mean()
    else:
        average_da = 0.0

    # Dofollow ratio
    if 'link_type' in df.columns:
        dofollow_count = df['link_type'].str.lower().str.contains('dofollow', na=False).sum()
        dofollow_ratio = (dofollow_count / total_backlinks) * 100
    else:
        dofollow_ratio = 50.0  # Default assumption

    # Toxic links (spam_score > 50 considered toxic)
    if 'spam_score' in df.columns:
        toxic_links = (df['spam_score'] > 50).sum()
    else:
        toxic_links = 0

    # Calculate health score (0-100)
    # Components:
    # - DA score (40%): 0-100 scale based on average DA
    # - Dofollow ratio (30%): percentage of dofollow links
    # - Toxicity penalty (30%): reduced by percentage of toxic links

    da_score = min(average_da, 100)  # DA already on 0-100 scale
    dofollow_score = dofollow_ratio  # Already percentage
    toxic_ratio = (toxic_links / total_backlinks) * 100 if total_backlinks > 0 else 0
    toxicity_score = max(0, 100 - toxic_ratio)  # Inverse of toxic ratio

    health_score = (da_score * 0.4) + (dofollow_score * 0.3) + (toxicity_score * 0.3)
    health_score = round(health_score, 1)

    return {
        "health_score": health_score,
        "metrics": {
            "total_backlinks": int(total_backlinks),
            "referring_domains": int(referring_domains),
            "average_da": round(average_da, 1),
            "dofollow_ratio": round(dofollow_ratio, 1),
            "toxic_links": int(toxic_links)
        }
    }


def score_technical(df: pd.DataFrame) -> dict:
    """
    Calculate technical health score (0-100) based on:
    - 4XX/5XX errors
    - Missing titles/meta descriptions
    - Thin content (<300 words)

    Expected columns: URL, Status Code, Title 1, Meta Description 1, Word Count
    """

    if df.empty:
        return {
            "health_score": 0,
            "critical_issues": [],
            "important_issues": [],
            "optimisations": []
        }

    total_pages = len(df)
    critical_issues = []
    important_issues = []
    optimisations = []

    # Normalise column names (handle variations in CSV exports)
    df.columns = df.columns.str.strip().str.lower()

    # Map common column name variations
    status_col = None
    for col in ['status code', 'statuscode', 'status_code', 'status']:
        if col in df.columns:
            status_col = col
            break

    title_col = None
    for col in ['title 1', 'title', 'title_1', 'page title']:
        if col in df.columns:
            title_col = col
            break

    meta_col = None
    for col in ['meta description 1', 'meta description', 'meta_description_1', 'description']:
        if col in df.columns:
            meta_col = col
            break

    word_count_col = None
    for col in ['word count', 'wordcount', 'word_count', 'words']:
        if col in df.columns:
            word_count_col = col
            break

    url_col = None
    for col in ['url', 'address', 'page']:
        if col in df.columns:
            url_col = col
            break

    # Count issues
    error_4xx_5xx = 0
    missing_titles = 0
    missing_meta = 0
    thin_content = 0

    if status_col:
        df[status_col] = pd.to_numeric(df[status_col], errors='coerce')
        error_4xx_5xx = ((df[status_col] >= 400) & (df[status_col] < 600)).sum()

        if error_4xx_5xx > 0:
            error_pages = df[df[status_col] >= 400][url_col].head(5).tolist() if url_col else []
            critical_issues.append({
                "issue": f"{error_4xx_5xx} pages with 4XX/5XX errors",
                "priority": "Critical",
                "affected_pages": len(error_pages),
                "examples": error_pages[:3]
            })

    if title_col:
        missing_titles = df[title_col].isna().sum() + (df[title_col].str.strip() == '').sum()

        if missing_titles > 0:
            missing_title_pages = df[df[title_col].isna() | (df[title_col].str.strip() == '')][url_col].head(5).tolist() if url_col else []
            important_issues.append({
                "issue": f"{missing_titles} pages missing title tags",
                "priority": "Important",
                "affected_pages": len(missing_title_pages),
                "examples": missing_title_pages[:3]
            })

    if meta_col:
        missing_meta = df[meta_col].isna().sum() + (df[meta_col].str.strip() == '').sum()

        if missing_meta > 0:
            optimisations.append({
                "issue": f"{missing_meta} pages missing meta descriptions",
                "priority": "Optimisation",
                "affected_pages": missing_meta
            })

    if word_count_col:
        df[word_count_col] = pd.to_numeric(df[word_count_col], errors='coerce')
        thin_content = (df[word_count_col] < 300).sum()

        if thin_content > 0:
            thin_pages = df[df[word_count_col] < 300][url_col].head(5).tolist() if url_col else []
            important_issues.append({
                "issue": f"{thin_content} pages with thin content (<300 words)",
                "priority": "Important",
                "affected_pages": len(thin_pages),
                "examples": thin_pages[:3]
            })

    # Calculate health score (0-100)
    # Higher percentage of issues = lower score
    error_penalty = (error_4xx_5xx / total_pages) * 100 if total_pages > 0 else 0
    missing_title_penalty = (missing_titles / total_pages) * 100 if total_pages > 0 else 0
    missing_meta_penalty = (missing_meta / total_pages) * 50 if total_pages > 0 else 0  # Less critical
    thin_content_penalty = (thin_content / total_pages) * 75 if total_pages > 0 else 0

    # Weight the penalties
    total_penalty = (error_penalty * 0.4) + (missing_title_penalty * 0.3) + \
                   (thin_content_penalty * 0.2) + (missing_meta_penalty * 0.1)

    health_score = max(0, 100 - total_penalty)
    health_score = round(health_score, 1)

    return {
        "health_score": health_score,
        "critical_issues": critical_issues,
        "important_issues": important_issues,
        "optimisations": optimisations
    }


def score_content_structure(df: pd.DataFrame) -> dict:
    """
    Calculate content structure score (0-100) based on:
    - Word count distribution
    - Title length heuristics

    Expected columns: URL, Title 1, Word Count
    """

    if df.empty:
        return {
            "score": 0,
            "pages_requiring_restructuring": 0,
            "quick_wins": []
        }

    total_pages = len(df)
    quick_wins = []
    pages_needing_work = 0

    # Normalise column names
    df.columns = df.columns.str.strip().str.lower()

    # Find relevant columns
    title_col = None
    for col in ['title 1', 'title', 'title_1', 'page title']:
        if col in df.columns:
            title_col = col
            break

    word_count_col = None
    for col in ['word count', 'wordcount', 'word_count', 'words']:
        if col in df.columns:
            word_count_col = col
            break

    # Analyse title lengths
    long_titles = 0
    short_titles = 0

    if title_col:
        df['title_length'] = df[title_col].str.len()
        long_titles = (df['title_length'] > 65).sum()
        short_titles = (df['title_length'] < 30).sum()

        if long_titles > 5:
            quick_wins.append(f"Shorten {long_titles} titles over 65 characters for better SERP display.")

        if short_titles > 5:
            quick_wins.append(f"Expand {short_titles} titles under 30 characters to be more descriptive.")

    # Analyse word count distribution
    if word_count_col:
        df[word_count_col] = pd.to_numeric(df[word_count_col], errors='coerce')

        # Pages with <300 words need expansion
        thin_pages = (df[word_count_col] < 300).sum()
        if thin_pages > 0:
            quick_wins.append(f"Expand {thin_pages} thin pages to at least 300 words.")
            pages_needing_work += thin_pages

        # Pages with 300-500 words could be improved
        moderate_pages = ((df[word_count_col] >= 300) & (df[word_count_col] < 500)).sum()
        pages_needing_work += moderate_pages

        # Check for good content (500+ words)
        good_content = (df[word_count_col] >= 500).sum()
        good_ratio = (good_content / total_pages) * 100 if total_pages > 0 else 0
    else:
        good_ratio = 50  # Default assumption

    # Calculate structure score
    # Based on:
    # - Percentage of pages with good word count (50%)
    # - Title optimisation (30%)
    # - Content consistency (20%)

    word_count_score = good_ratio if word_count_col else 50

    if title_col:
        title_issues_ratio = ((long_titles + short_titles) / total_pages) * 100 if total_pages > 0 else 0
        title_score = max(0, 100 - title_issues_ratio)
    else:
        title_score = 50

    # Consistency: fewer pages needing work = better consistency
    consistency_ratio = (pages_needing_work / total_pages) * 100 if total_pages > 0 else 0
    consistency_score = max(0, 100 - consistency_ratio)

    structure_score = (word_count_score * 0.5) + (title_score * 0.3) + (consistency_score * 0.2)
    structure_score = round(structure_score, 1)

    if not quick_wins:
        quick_wins.append("Content structure is well optimised. Continue monitoring.")

    return {
        "score": structure_score,
        "pages_requiring_restructuring": int(pages_needing_work),
        "quick_wins": quick_wins[:5]  # Limit to top 5
    }


def project_roi(
    backlink_score: float,
    technical_score: float,
    content_structure_score: float,
    monthly_traffic: int,
    conversion_rate: float,
    avg_order_value: float,
    investment_amount: float
) -> dict:
    """
    Calculate ROI projections based on health scores and business metrics.

    Uses weighted scoring:
    - Backlink: 30%
    - Technical: 25%
    - AI Visibility: 25% (baseline 30% for MVP)
    - Content Structure: 20%
    """

    # AI visibility baseline for MVP (will be replaced in Stage 3)
    ai_visibility_baseline = 30.0

    # Calculate overall health score
    overall_health = (
        (backlink_score * 0.30) +
        (technical_score * 0.25) +
        (ai_visibility_baseline * 0.25) +
        (content_structure_score * 0.20)
    )

    # Calculate improvement potential (gap from 100%)
    improvement_potential = (100 - overall_health) / 100

    # Traffic uplift estimation
    # Each 10 points of improvement = ~5-15% traffic increase
    # Using conservative 7% per 10 points
    traffic_uplift_percentage = improvement_potential * 70  # Up to 70% increase possible

    additional_monthly_traffic = int(monthly_traffic * (traffic_uplift_percentage / 100))

    # Revenue calculations
    # Additional conversions from new traffic
    additional_conversions = additional_monthly_traffic * (conversion_rate / 100)
    additional_monthly_revenue = additional_conversions * avg_order_value

    # Annual projection
    annual_revenue_increase = additional_monthly_revenue * 12

    # ROI calculation
    roi_percent = ((annual_revenue_increase - investment_amount) / investment_amount) * 100 if investment_amount > 0 else 0

    return {
        "additional_monthly_traffic": int(additional_monthly_traffic),
        "additional_monthly_revenue": round(additional_monthly_revenue, 2),
        "annual_revenue_increase": round(annual_revenue_increase, 2),
        "roi_percent": round(roi_percent, 1),
        "overall_health_score": round(overall_health, 1)
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML form for SEO analysis"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en-GB">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEO & AI Visibility Analysis Tool</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
            }
            h1 {
                color: #667eea;
                font-size: 28px;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #444;
                font-size: 14px;
            }
            input[type="text"],
            input[type="number"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus,
            input[type="number"]:focus {
                outline: none;
                border-color: #667eea;
            }
            input[type="file"] {
                width: 100%;
                padding: 10px;
                border: 2px dashed #e0e0e0;
                border-radius: 6px;
                background: #f9f9f9;
                cursor: pointer;
                font-size: 14px;
            }
            input[type="file"]:hover {
                border-color: #667eea;
                background: #f0f0ff;
            }
            .file-hint {
                font-size: 12px;
                color: #888;
                margin-top: 5px;
            }
            .row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                margin-top: 10px;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            .info-box {
                background: #f0f7ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 25px;
                border-radius: 4px;
                font-size: 13px;
                color: #555;
            }
            .info-box strong {
                color: #667eea;
            }
            @media (max-width: 600px) {
                .row {
                    grid-template-columns: 1fr;
                }
                .container {
                    padding: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SEO & AI Visibility Analysis Tool</h1>
            <p class="subtitle">Analyse your website's SEO health and project potential ROI</p>

            <div class="info-box">
                <strong>Instructions:</strong> Complete all fields below and upload your Screaming Frog crawl export and backlink data CSV.
                The tool will analyse your site's technical health, backlink profile, and content structure, then provide actionable recommendations.
            </div>

            <form action="/analyse-form" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="website_url">Website URL</label>
                    <input type="text" id="website_url" name="website_url" placeholder="https://example.com" required>
                </div>

                <div class="row">
                    <div class="form-group">
                        <label for="monthly_traffic">Monthly Traffic (visitors)</label>
                        <input type="number" id="monthly_traffic" name="monthly_traffic" placeholder="10000" required min="0">
                    </div>
                    <div class="form-group">
                        <label for="conversion_rate">Conversion Rate (%)</label>
                        <input type="number" id="conversion_rate" name="conversion_rate" placeholder="2.5" required min="0" step="0.01">
                    </div>
                </div>

                <div class="row">
                    <div class="form-group">
                        <label for="avg_order_value">Average Order Value (£)</label>
                        <input type="number" id="avg_order_value" name="avg_order_value" placeholder="50.00" required min="0" step="0.01">
                    </div>
                    <div class="form-group">
                        <label for="investment_amount">Investment Amount (£)</label>
                        <input type="number" id="investment_amount" name="investment_amount" placeholder="5000.00" required min="0" step="0.01">
                    </div>
                </div>

                <div class="form-group">
                    <label for="sf_file">Screaming Frog CSV Export</label>
                    <input type="file" id="sf_file" name="sf_file" accept=".csv" required>
                    <div class="file-hint">Must contain: URL, Status Code, Title 1, Meta Description 1, Word Count</div>
                </div>

                <div class="form-group">
                    <label for="backlink_file">Backlink CSV File</label>
                    <input type="file" id="backlink_file" name="backlink_file" accept=".csv" required>
                    <div class="file-hint">Must contain: source_url, domain_authority, link_type, spam_score</div>
                </div>

                <button type="submit">Analyse Website</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/analyse-form", response_class=HTMLResponse)
async def analyse_form(
    website_url: str = Form(...),
    monthly_traffic: int = Form(...),
    conversion_rate: float = Form(...),
    avg_order_value: float = Form(...),
    investment_amount: float = Form(...),
    sf_file: UploadFile = File(...),
    backlink_file: UploadFile = File(...)
):
    """
    Analyse SEO health and project ROI - Returns HTML report.

    Accepts:
    - Form fields: website_url, monthly_traffic, conversion_rate, avg_order_value, investment_amount
    - Files: sf_file (Screaming Frog export), backlink_file (backlink data)

    Returns: HTML report with scores, issues, and ROI projections
    """

    try:
        # Read Screaming Frog CSV
        sf_content = await sf_file.read()
        sf_df = pd.read_csv(io.BytesIO(sf_content))

        # Read Backlink CSV
        backlink_content = await backlink_file.read()
        backlink_df = pd.read_csv(io.BytesIO(backlink_content))

        # Calculate scores
        backlink_results = score_backlinks(backlink_df)
        technical_results = score_technical(sf_df)
        content_structure_results = score_content_structure(sf_df)

        # Calculate ROI
        roi_results = project_roi(
            backlink_score=backlink_results["health_score"],
            technical_score=technical_results["health_score"],
            content_structure_score=content_structure_results["score"],
            monthly_traffic=monthly_traffic,
            conversion_rate=conversion_rate,
            avg_order_value=avg_order_value,
            investment_amount=investment_amount
        )

        # Extract overall health score from ROI results
        overall_health_score = roi_results.pop("overall_health_score")

        # Generate HTML report
        def get_score_color(score):
            if score >= 80: return "#10b981"
            elif score >= 60: return "#f59e0b"
            else: return "#ef4444"

        def get_score_status(score):
            if score >= 80: return "Excellent"
            elif score >= 60: return "Good"
            elif score >= 40: return "Needs Improvement"
            else: return "Critical"

        html_report = f"""
        <!DOCTYPE html>
        <html lang="en-GB">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SEO Analysis Report - {website_url}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    padding: 40px;
                }}
                h1 {{
                    color: #667eea;
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                .website-url {{
                    color: #666;
                    font-size: 18px;
                    margin-bottom: 30px;
                }}
                .back-link {{
                    display: inline-block;
                    margin-bottom: 20px;
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 600;
                }}
                .back-link:hover {{
                    text-decoration: underline;
                }}
                .overall-score {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .overall-score h2 {{
                    font-size: 18px;
                    margin-bottom: 15px;
                    opacity: 0.9;
                }}
                .overall-score .score {{
                    font-size: 64px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .overall-score .status {{
                    font-size: 20px;
                    opacity: 0.9;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 25px;
                }}
                .card h3 {{
                    font-size: 18px;
                    margin-bottom: 15px;
                    color: #444;
                }}
                .score-display {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }}
                .score-number {{
                    font-size: 48px;
                    font-weight: bold;
                }}
                .score-label {{
                    font-size: 14px;
                    color: #666;
                }}
                .metric-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #f0f0f0;
                }}
                .metric-label {{
                    color: #666;
                    font-size: 14px;
                }}
                .metric-value {{
                    font-weight: 600;
                    color: #333;
                }}
                .issue-list {{
                    list-style: none;
                }}
                .issue-item {{
                    padding: 12px;
                    margin-bottom: 10px;
                    border-radius: 6px;
                    background: #f9f9f9;
                    border-left: 4px solid #666;
                }}
                .issue-item.critical {{
                    background: #fef2f2;
                    border-left-color: #ef4444;
                }}
                .issue-item.important {{
                    background: #fffbeb;
                    border-left-color: #f59e0b;
                }}
                .issue-item.optimisation {{
                    background: #f0f9ff;
                    border-left-color: #3b82f6;
                }}
                .issue-priority {{
                    font-size: 11px;
                    font-weight: 600;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                .issue-description {{
                    font-size: 14px;
                    color: #333;
                }}
                .quick-win {{
                    padding: 10px 15px;
                    margin-bottom: 8px;
                    background: #f0fdf4;
                    border-left: 4px solid #10b981;
                    border-radius: 4px;
                    font-size: 14px;
                }}
                .roi-section {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin-top: 30px;
                }}
                .roi-section h2 {{
                    font-size: 24px;
                    margin-bottom: 20px;
                }}
                .roi-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }}
                .roi-metric {{
                    text-align: center;
                }}
                .roi-value {{
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .roi-label {{
                    font-size: 14px;
                    opacity: 0.9;
                }}
                @media print {{
                    body {{
                        background: white;
                    }}
                    .back-link {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/" class="back-link">← Analyse Another Website</a>

                <h1>SEO Analysis Report</h1>
                <div class="website-url">{website_url}</div>

                <div class="overall-score">
                    <h2>Overall Health Score</h2>
                    <div class="score">{overall_health_score}</div>
                    <div class="status">{get_score_status(overall_health_score)}</div>
                </div>

                <div class="grid">
                    <!-- Backlink Health -->
                    <div class="card">
                        <h3>Backlink Health Score</h3>
                        <div class="score-display">
                            <span class="score-number" style="color: {get_score_color(backlink_results['health_score'])}">{backlink_results['health_score']}</span>
                            <span class="score-label">/100</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Total Backlinks</span>
                            <span class="metric-value">{backlink_results['metrics']['total_backlinks']:,}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Referring Domains</span>
                            <span class="metric-value">{backlink_results['metrics']['referring_domains']:,}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Average Domain Authority</span>
                            <span class="metric-value">{backlink_results['metrics']['average_da']}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Dofollow Ratio</span>
                            <span class="metric-value">{backlink_results['metrics']['dofollow_ratio']}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Toxic Links</span>
                            <span class="metric-value">{backlink_results['metrics']['toxic_links']}</span>
                        </div>
                    </div>

                    <!-- Technical Health -->
                    <div class="card">
                        <h3>Technical Health Score</h3>
                        <div class="score-display">
                            <span class="score-number" style="color: {get_score_color(technical_results['health_score'])}">{technical_results['health_score']}</span>
                            <span class="score-label">/100</span>
                        </div>
                        <h4 style="font-size: 14px; margin-top: 20px; margin-bottom: 10px; color: #666;">Issues Found:</h4>
                        <ul class="issue-list">
                            {"".join([f'<li class="issue-item critical"><div class="issue-priority" style="color: #ef4444;">Critical</div><div class="issue-description">{issue["issue"]}</div></li>' for issue in technical_results['critical_issues']])}
                            {"".join([f'<li class="issue-item important"><div class="issue-priority" style="color: #f59e0b;">Important</div><div class="issue-description">{issue["issue"]}</div></li>' for issue in technical_results['important_issues']])}
                            {"".join([f'<li class="issue-item optimisation"><div class="issue-priority" style="color: #3b82f6;">Optimisation</div><div class="issue-description">{issue["issue"]}</div></li>' for issue in technical_results['optimisations']])}
                        </ul>
                        {'' if (technical_results['critical_issues'] or technical_results['important_issues'] or technical_results['optimisations']) else '<p style="color: #10b981; font-weight: 600;">No issues found!</p>'}
                    </div>

                    <!-- Content Structure -->
                    <div class="card">
                        <h3>Content Structure Score</h3>
                        <div class="score-display">
                            <span class="score-number" style="color: {get_score_color(content_structure_results['score'])}">{content_structure_results['score']}</span>
                            <span class="score-label">/100</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Pages Requiring Work</span>
                            <span class="metric-value">{content_structure_results['pages_requiring_restructuring']}</span>
                        </div>
                        <h4 style="font-size: 14px; margin-top: 20px; margin-bottom: 10px; color: #666;">Quick Wins:</h4>
                        {"".join([f'<div class="quick-win">{win}</div>' for win in content_structure_results['quick_wins']])}
                    </div>
                </div>

                <!-- ROI Projection -->
                <div class="roi-section">
                    <h2>ROI Projection (12 Months)</h2>
                    <div class="roi-grid">
                        <div class="roi-metric">
                            <div class="roi-value">+{roi_results['additional_monthly_traffic']:,}</div>
                            <div class="roi-label">Additional Monthly Traffic</div>
                        </div>
                        <div class="roi-metric">
                            <div class="roi-value">£{roi_results['additional_monthly_revenue']:,.2f}</div>
                            <div class="roi-label">Additional Monthly Revenue</div>
                        </div>
                        <div class="roi-metric">
                            <div class="roi-value">£{roi_results['annual_revenue_increase']:,.2f}</div>
                            <div class="roi-label">Annual Revenue Increase</div>
                        </div>
                        <div class="roi-metric">
                            <div class="roi-value">{roi_results['roi_percent']:,.1f}%</div>
                            <div class="roi-label">ROI</div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_report)

    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html lang="en-GB">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Analysis Error</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .error-container {{
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    max-width: 600px;
                    text-align: center;
                }}
                h1 {{
                    color: #ef4444;
                    margin-bottom: 20px;
                }}
                p {{
                    color: #666;
                    margin-bottom: 30px;
                }}
                .error-detail {{
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    padding: 15px;
                    border-radius: 6px;
                    font-family: monospace;
                    font-size: 14px;
                    margin-bottom: 20px;
                    text-align: left;
                }}
                a {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Analysis Failed</h1>
                <p>There was an error processing your files. Please check the file formats and try again.</p>
                <div class="error-detail">{str(e)}</div>
                <a href="/">← Back to Form</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)


@app.post("/analyse")
async def analyse(
    website_url: str = Form(...),
    monthly_traffic: int = Form(...),
    conversion_rate: float = Form(...),
    avg_order_value: float = Form(...),
    investment_amount: float = Form(...),
    sf_file: UploadFile = File(...),
    backlink_file: UploadFile = File(...)
):
    """
    Analyse SEO health and project ROI.

    Accepts:
    - Form fields: website_url, monthly_traffic, conversion_rate, avg_order_value, investment_amount
    - Files: sf_file (Screaming Frog export), backlink_file (backlink data)

    Returns: JSON with scores, issues, and ROI projections
    """

    try:
        # Read Screaming Frog CSV
        sf_content = await sf_file.read()
        sf_df = pd.read_csv(io.BytesIO(sf_content))

        # Read Backlink CSV
        backlink_content = await backlink_file.read()
        backlink_df = pd.read_csv(io.BytesIO(backlink_content))

        # Calculate scores
        backlink_results = score_backlinks(backlink_df)
        technical_results = score_technical(sf_df)
        content_structure_results = score_content_structure(sf_df)

        # Calculate ROI
        roi_results = project_roi(
            backlink_score=backlink_results["health_score"],
            technical_score=technical_results["health_score"],
            content_structure_score=content_structure_results["score"],
            monthly_traffic=monthly_traffic,
            conversion_rate=conversion_rate,
            avg_order_value=avg_order_value,
            investment_amount=investment_amount
        )

        # Extract overall health score from ROI results
        overall_health_score = roi_results.pop("overall_health_score")

        # Build response
        response = {
            "website": website_url,
            "overall_health_score": overall_health_score,
            "backlinks": backlink_results,
            "technical": technical_results,
            "content_structure": content_structure_results,
            "roi_projection": roi_results
        }

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Analysis failed",
                "detail": str(e)
            }
        )


@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "operational",
        "service": "SEO & AI Visibility Analysis Tool",
        "version": "2.0.0 - Stage 2"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
