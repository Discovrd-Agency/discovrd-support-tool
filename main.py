"""
SEO & AI Visibility Analysis Tool - Stage 1
FastAPI backend for analysing backlinks, technical SEO, and content structure
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "SEO & AI Visibility Analysis Tool",
        "version": "1.0.0 - Stage 1"
    }


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
