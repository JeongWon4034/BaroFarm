"""
FreshGrowth Analytics API (FastAPI)
================================================
kpi.py(단일 분석 엔진)를 JSON으로 노출해, Vue 판매자 대시보드가 호출한다.
Streamlit은 kpi.py를 직접 import하고, Vue는 이 API를 통해 같은 엔진을 공유한다.

  MySQL+MongoDB ─load_data()→ kpi.py ─┬─ Streamlit (직접 import)
                                       └─ FastAPI(이 파일) → Vue 대시보드

실행:  uvicorn api:app --reload --port 8000
문서:  http://localhost:8000/docs

데이터 소스: 현재는 data/ 합성 CSV. load_data()를 DB 로더로 교체하면
            엔드포인트 코드 변경 없이 라이브 전환된다(순수 함수 설계의 보상).
"""
from __future__ import annotations

import math
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import kpi

app = FastAPI(title="FreshGrowth Analytics API", version="1.0")

# Vue dev 서버(예: 5173)에서 직접 호출 허용. 운영에선 도메인을 좁힌다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── 데이터 로드 (캐시) ─────────────────────────────────────────────
@lru_cache(maxsize=1)
def _data():
    """data/ 산출물을 1회 로드해 캐시. /refresh로 캐시를 비워 재로딩."""
    return kpi.load_data()


def _records(df: pd.DataFrame) -> list[dict]:
    """DataFrame → JSON 직렬화. NaN/Inf는 JSON 무효라 None으로 치환."""
    out = df.to_dict(orient="records")
    for row in out:
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                row[k] = None
    return out


# ── 엔드포인트 ─────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/refresh")
def refresh():
    """데이터 캐시 무효화(라이브 DB 전환 후 최신 반영용)."""
    _data.cache_clear()
    return {"refreshed": True}


@app.get("/analytics/summary")
def summary():
    """판매자 대시보드 상단 KPI 카드용 핵심 지표 묶음."""
    d = _data()
    rv = kpi.revenue(d["orders"])
    f = kpi.funnel(d["events"])
    de = kpi.deal_effect(d["events"])
    rp = kpi.repurchase_rate(d["orders"])
    purchase_conv = float(f.loc[f["stage"] == "purchase", "conv_from_top"].iloc[0])
    return {
        "gmv": rv["gmv"],
        "orders": rv["orders"],
        "aov": rv["aov"],
        "session_to_purchase": purchase_conv,
        "repurchase_rate": rp["rate"],
        "deal_lift": de["lift"],
        "deal_significant": de["test"]["significant"],
    }


@app.get("/analytics/funnel")
def funnel():
    return _records(kpi.funnel(_data()["events"]))


@app.get("/analytics/deal-effect")
def deal_effect():
    return kpi.deal_effect(_data()["events"])


@app.get("/analytics/revenue")
def revenue():
    rv = kpi.revenue(_data()["orders"])
    return {
        "gmv": rv["gmv"], "orders": rv["orders"], "aov": rv["aov"],
        "daily": _records(rv["daily"].assign(date=rv["daily"]["date"].astype(str))),
    }


@app.get("/analytics/repurchase")
def repurchase():
    return kpi.repurchase_rate(_data()["orders"])


@app.get("/analytics/cohort")
def cohort():
    d = _data()
    cr = kpi.cohort_retention(d["orders"], d["users"])
    cr = cr.assign(cohort=cr["cohort"].astype(str))
    return _records(cr)


@app.get("/analytics/category")
def category():
    d = _data()
    return _records(kpi.category_performance(d["orders"], d["products"]))


@app.get("/analytics/products")
def products(top: int = Query(20, ge=1, le=200)):
    d = _data()
    return _records(kpi.product_performance(d["events"], d["orders"], d["products"], top=top))
