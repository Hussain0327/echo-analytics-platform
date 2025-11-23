from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional, Dict, Any
import pandas as pd
import io

from app.services.metrics.registry import (
    create_metrics_engine,
    create_revenue_engine,
    create_marketing_engine,
    get_available_metrics,
)
from app.services.metrics.base import MetricResult, MetricDefinition
from app.services.metrics.timeseries import TimeSeriesAnalyzer


router = APIRouter()


@router.get("/available")
async def list_available_metrics() -> Dict[str, List[str]]:
    return get_available_metrics()


@router.post("/calculate/csv")
async def calculate_from_csv(
    file: UploadFile = File(...),
    metrics: Optional[str] = Query(None, description="Comma-separated metric names, or 'all'"),
    category: Optional[str] = Query(None, description="Category: revenue, financial, marketing"),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    if not content or content.strip() == b'':
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        df = pd.read_csv(io.BytesIO(content))
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="File is empty")

    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty")

    engine = create_metrics_engine(df)
    results = []

    if metrics and metrics != 'all':
        metric_list = [m.strip() for m in metrics.split(',')]
        for metric_name in metric_list:
            try:
                result = engine.calculate(metric_name)
                results.append(result.model_dump())
            except ValueError as e:
                results.append({
                    'metric_name': metric_name,
                    'error': str(e)
                })
    else:
        calculated = engine.calculate_all(category=category)
        results = [r.model_dump() for r in calculated]

    return {
        'file': file.filename,
        'rows': len(df),
        'columns': list(df.columns),
        'metrics_calculated': len(results),
        'results': results
    }


@router.post("/calculate/revenue")
async def calculate_revenue_metrics(
    file: UploadFile = File(...),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty")

    engine = create_revenue_engine(df)
    calculated = engine.calculate_all()

    return {
        'file': file.filename,
        'rows': len(df),
        'category': 'revenue',
        'metrics_calculated': len(calculated),
        'results': [r.model_dump() for r in calculated]
    }


@router.post("/calculate/marketing")
async def calculate_marketing_metrics(
    file: UploadFile = File(...),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty")

    engine = create_marketing_engine(df)
    calculated = engine.calculate_all()

    return {
        'file': file.filename,
        'rows': len(df),
        'category': 'marketing',
        'metrics_calculated': len(calculated),
        'results': [r.model_dump() for r in calculated]
    }


@router.post("/trend")
async def analyze_trend(
    file: UploadFile = File(...),
    value_column: str = Query(..., description="Column to analyze"),
    date_column: str = Query('date', description="Date column name"),
    period: str = Query('month', description="Period: day, week, month, quarter, year"),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    if value_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{value_column}' not found")

    if date_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Date column '{date_column}' not found")

    analyzer = TimeSeriesAnalyzer(df, date_column)

    return {
        'file': file.filename,
        'value_column': value_column,
        'trend': analyzer.detect_trend(value_column, period),
        'comparison': analyzer.period_comparison(value_column, period),
        'date_range': analyzer.get_date_range()
    }


@router.post("/growth")
async def calculate_growth(
    file: UploadFile = File(...),
    value_column: str = Query(..., description="Column to analyze"),
    date_column: str = Query('date', description="Date column name"),
    period: str = Query('month', description="Period: day, week, month, quarter, year"),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    if value_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{value_column}' not found")

    analyzer = TimeSeriesAnalyzer(df, date_column)
    growth_df = analyzer.calculate_growth(value_column, period)

    growth_df.index = growth_df.index.astype(str)
    growth_data = growth_df.to_dict('index')

    return {
        'file': file.filename,
        'value_column': value_column,
        'period': period,
        'growth_data': growth_data
    }
