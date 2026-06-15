"""
FreshGrowth Growth KPI 계산 모듈
================================================
simulate.py가 만든 data/ 산출물 위에서 README §9 Growth 지표를
**실제 계산**으로 산출한다. (데이터는 합성, 수치는 실측)

설계 원칙
  - 모든 함수는 순수 함수: DataFrame in → 지표(DataFrame/dict) out.
    부수효과·전역상태·차트 코드 없음 → app.py(Streamlit)가 import해서 시각화만 담당.
  - 의존성 최소화: pandas + numpy만. 통계검정(2-비율 Z검정)은 직접 구현.

제공 지표
  1. funnel()              퍼널 전환율 (list_view→detail_view→purchase, 세션 기준)
  2. deal_effect()         마감임박 딜 효과 + 2-비율 Z검정  ⭐ 프로젝트 시그니처
  3. revenue()             GMV / 주문수 / 객단가(AOV) + 일별 시계열
  4. repurchase_rate()     재구매율 (2회 이상 구매한 구매자 비중)
  5. cohort_retention()    가입 주차 코호트 × N주 후 재구매 리텐션
  6. category_performance()카테고리별 주문·GMV·AOV
  7. product_performance() 상품별 조회→상세→구매 퍼널 + GMV (상위 N)
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# 퍼널 핵심 단계 (세션 기준 유니크 카운트). search·wishlist는 본류가 아니라 제외.
FUNNEL_STAGES = ["list_view", "detail_view", "purchase"]


# ──────────────────────────────────────────────────────────────────
# 로딩
# ──────────────────────────────────────────────────────────────────
def load_data(data_dir: str | None = None) -> dict[str, pd.DataFrame]:
    """data/ 산출물을 읽어 DataFrame 딕셔너리로 반환. 날짜 컬럼은 datetime 파싱."""
    d = data_dir or DATA_DIR
    if not os.path.exists(os.path.join(d, "events.ndjson")):
        raise FileNotFoundError(
            f"{d}에 데이터가 없습니다. 먼저 `python3 simulate.py`를 실행하세요."
        )

    events = pd.read_json(os.path.join(d, "events.ndjson"), lines=True)
    events["ts"] = pd.to_datetime(events["ts"])
    if "is_deal" in events:
        events["is_deal"] = events["is_deal"].fillna(False).astype(bool)

    users = pd.read_csv(os.path.join(d, "users.csv"), parse_dates=["created_at"])
    products = pd.read_csv(os.path.join(d, "products.csv"))
    orders = pd.read_csv(os.path.join(d, "orders.csv"), parse_dates=["order_date"])
    wishlists = pd.read_csv(os.path.join(d, "wishlists.csv"), parse_dates=["created_at"])
    reviews = pd.read_csv(os.path.join(d, "reviews.csv"), parse_dates=["created_at"])

    return {"events": events, "users": users, "products": products,
            "orders": orders, "wishlists": wishlists, "reviews": reviews}


# ──────────────────────────────────────────────────────────────────
# 1. 퍼널 전환율
# ──────────────────────────────────────────────────────────────────
def funnel(events: pd.DataFrame, stages: list[str] | None = None) -> pd.DataFrame:
    """단계별 도달 세션 수와 전환율. (퍼널은 세션 단위 유니크 기준)

    반환 컬럼: stage, sessions, conv_from_top(%), conv_from_prev(%)
    """
    stages = stages or FUNNEL_STAGES
    rows = []
    prev = None
    top = None
    for st in stages:
        n = events.loc[events["event_type"] == st, "session_id"].nunique()
        top = n if top is None else top
        rows.append({
            "stage": st,
            "sessions": n,
            "conv_from_top": round(n / top * 100, 2) if top else 0.0,
            "conv_from_prev": round(n / prev * 100, 2) if prev else 100.0,
        })
        prev = n
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────
# 2. 마감임박 딜 효과 (시그니처) + 2-비율 Z검정
# ──────────────────────────────────────────────────────────────────
def two_proportion_ztest(x1: int, n1: int, x2: int, n2: int) -> dict:
    """2-비율 Z검정. 그룹1=처치(딜), 그룹2=대조(정상).

    H0: p1 == p2,  H1(단측): p1 > p2
    반환: p1, p2, lift, z, p_value_one_sided, p_value_two_sided, significant(α=.05)
    """
    p1 = x1 / n1 if n1 else 0.0
    p2 = x2 / n2 if n2 else 0.0
    pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) else 0.0
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2)) if pooled and n1 and n2 else 0.0
    z = (p1 - p2) / se if se else 0.0
    phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))     # 표준정규 CDF
    p_one = 1 - phi
    p_two = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return {
        "p1": round(p1 * 100, 2), "p2": round(p2 * 100, 2),
        "lift": round(p1 / p2, 3) if p2 else None,
        "z": round(z, 3),
        "p_value_one_sided": round(p_one, 5),
        "p_value_two_sided": round(p_two, 5),
        "significant": p_two < 0.05,
    }


def deal_effect(events: pd.DataFrame) -> dict:
    """마감임박 딜 vs 정상가의 상세→구매 전환율 비교 + Z검정.

    denominator = detail_view 이벤트 수(딜/정상 구분), numerator = purchase 이벤트 수.
    반환: deal/normal 카운트 + two_proportion_ztest 결과(test 키).
    """
    d = events[events["event_type"].isin(["detail_view", "purchase"])]
    deal = d[d["is_deal"]]
    norm = d[~d["is_deal"]]

    def split(df):
        return (int((df["event_type"] == "detail_view").sum()),
                int((df["event_type"] == "purchase").sum()))

    n_deal_detail, n_deal_buy = split(deal)
    n_norm_detail, n_norm_buy = split(norm)
    test = two_proportion_ztest(n_deal_buy, n_deal_detail, n_norm_buy, n_norm_detail)
    return {
        "deal": {"detail": n_deal_detail, "purchase": n_deal_buy, "cvr": test["p1"]},
        "normal": {"detail": n_norm_detail, "purchase": n_norm_buy, "cvr": test["p2"]},
        "lift": test["lift"],
        "test": test,
    }


# ──────────────────────────────────────────────────────────────────
# 3. GMV / AOV
# ──────────────────────────────────────────────────────────────────
def revenue(orders: pd.DataFrame) -> dict:
    """전체 GMV·주문수·AOV와 일별 시계열(daily DataFrame)."""
    done = orders[orders["status"] == "COMPLETED"]
    gmv = int(done["total_price"].sum())
    n = int(len(done))
    daily = (done.assign(date=done["order_date"].dt.date)
                 .groupby("date")
                 .agg(orders=("order_id", "count"), gmv=("total_price", "sum"))
                 .reset_index())
    daily["aov"] = (daily["gmv"] / daily["orders"]).round(0).astype(int)
    return {
        "gmv": gmv,
        "orders": n,
        "aov": int(gmv / n) if n else 0,
        "daily": daily,
    }


# ──────────────────────────────────────────────────────────────────
# 4. 재구매율
# ──────────────────────────────────────────────────────────────────
def repurchase_rate(orders: pd.DataFrame) -> dict:
    """2회 이상 구매한 구매자 비중. 반환: buyers, repurchasers, rate(%)."""
    done = orders[orders["status"] == "COMPLETED"]
    per_buyer = done.groupby("buyer_id")["order_id"].count()
    buyers = int(len(per_buyer))
    repurch = int((per_buyer >= 2).sum())
    return {
        "buyers": buyers,
        "repurchasers": repurch,
        "rate": round(repurch / buyers * 100, 2) if buyers else 0.0,
        "orders_per_buyer": round(per_buyer.mean(), 2) if buyers else 0.0,
    }


# ──────────────────────────────────────────────────────────────────
# 5. 코호트 리텐션 (가입 주차 × N주 후 재구매)
# ──────────────────────────────────────────────────────────────────
def cohort_retention(orders: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    """가입 주차를 코호트로, 가입 후 N주차에 구매한 구매자 비율(%) 매트릭스.

    행=cohort(가입 주 월요일), 열=week_0..week_k, 값=리텐션 %. Week 0 = 가입 주.
    """
    buyers = users[users["role"] == "BUYER"].copy()
    buyers["cohort"] = buyers["created_at"].dt.to_period("W").dt.start_time
    cohort_of = buyers.set_index("user_id")["cohort"]
    cohort_size = buyers.groupby("cohort")["user_id"].nunique()

    done = orders[orders["status"] == "COMPLETED"].copy()
    done["cohort"] = done["buyer_id"].map(cohort_of)
    done = done.dropna(subset=["cohort"])
    done["order_week"] = done["order_date"].dt.to_period("W").dt.start_time
    done["week_no"] = ((done["order_week"] - done["cohort"]).dt.days // 7)
    done = done[done["week_no"] >= 0]

    active = (done.groupby(["cohort", "week_no"])["buyer_id"].nunique()
                  .reset_index(name="active"))
    active["size"] = active["cohort"].map(cohort_size)
    active["retention"] = (active["active"] / active["size"] * 100).round(1)

    matrix = (active.pivot(index="cohort", columns="week_no", values="retention")
                    .sort_index())
    matrix.columns = [f"week_{c}" for c in matrix.columns]
    matrix.insert(0, "cohort_size", cohort_size.reindex(matrix.index).astype(int).values)
    return matrix.reset_index()


# ──────────────────────────────────────────────────────────────────
# 6. 카테고리별 성과
# ──────────────────────────────────────────────────────────────────
def category_performance(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """카테고리별 주문수·GMV·AOV·딜 비중."""
    done = orders[orders["status"] == "COMPLETED"].merge(
        products[["product_id", "category"]], on="product_id", how="left")
    g = (done.groupby("category")
             .agg(orders=("order_id", "count"),
                  gmv=("total_price", "sum"),
                  deal_orders=("is_deal", "sum"))
             .reset_index())
    g["aov"] = (g["gmv"] / g["orders"]).round(0).astype(int)
    g["deal_share"] = (g["deal_orders"] / g["orders"] * 100).round(1)
    return g.sort_values("gmv", ascending=False).reset_index(drop=True)


# ──────────────────────────────────────────────────────────────────
# 7. 상품별 성과 (퍼널 + GMV, 상위 N)
# ──────────────────────────────────────────────────────────────────
def product_performance(events: pd.DataFrame, orders: pd.DataFrame,
                        products: pd.DataFrame, top: int = 20) -> pd.DataFrame:
    """상품별 조회·상세·구매 카운트와 상세→구매 전환율, GMV. GMV 상위 top개."""
    ev = events.dropna(subset=["product_id"]).copy()
    ev["product_id"] = ev["product_id"].astype(int)
    counts = (ev.pivot_table(index="product_id", columns="event_type",
                             values="event_id", aggfunc="count", fill_value=0))
    for col in ["list_view", "detail_view", "purchase"]:
        if col not in counts:
            counts[col] = 0

    done = orders[orders["status"] == "COMPLETED"]
    gmv = done.groupby("product_id")["total_price"].sum()

    out = pd.DataFrame({
        "list_view": counts["list_view"],
        "detail_view": counts["detail_view"],
        "purchase": counts["purchase"],
    })
    out["detail_to_buy"] = (out["purchase"] / out["detail_view"]
                            .replace(0, np.nan) * 100).round(2)
    out["gmv"] = gmv
    out = out.merge(products[["product_id", "name", "category"]],
                    left_index=True, right_on="product_id", how="left")
    out["gmv"] = out["gmv"].fillna(0).astype(int)
    cols = ["product_id", "name", "category", "list_view", "detail_view",
            "purchase", "detail_to_buy", "gmv"]
    return out[cols].sort_values("gmv", ascending=False).head(top).reset_index(drop=True)


# ──────────────────────────────────────────────────────────────────
# CLI — 단독 실행 시 모든 KPI 요약 출력 (검증용)
# ──────────────────────────────────────────────────────────────────
def main():
    data = load_data()
    ev, od = data["events"], data["orders"]

    print("=" * 60)
    print("  FreshGrowth Growth KPI 요약")
    print("=" * 60)

    print("\n[1] 퍼널 (세션 기준)")
    f = funnel(ev)
    for _, r in f.iterrows():
        print(f"    {r['stage']:<12} {r['sessions']:>7,} 세션  "
              f"(top {r['conv_from_top']:>5.1f}% / prev {r['conv_from_prev']:>5.1f}%)")

    print("\n[2] 마감임박 딜 효과 (상세→구매)  ⭐ 시그니처")
    de = deal_effect(ev)
    t = de["test"]
    print(f"    딜    {de['deal']['cvr']:>5.2f}%  ({de['deal']['purchase']}/{de['deal']['detail']})")
    print(f"    정상  {de['normal']['cvr']:>5.2f}%  ({de['normal']['purchase']}/{de['normal']['detail']})")
    print(f"    lift ×{de['lift']}  |  Z={t['z']}  p(단측)={t['p_value_one_sided']}  "
          f"→ {'H0 기각 ✅' if t['significant'] else 'H0 유지'}")

    print("\n[3] 매출")
    rv = revenue(od)
    print(f"    GMV {rv['gmv']:>12,}원  |  주문 {rv['orders']:,}건  |  AOV {rv['aov']:,}원")

    print("\n[4] 재구매율")
    rp = repurchase_rate(od)
    print(f"    {rp['rate']}%  ({rp['repurchasers']}/{rp['buyers']} 구매자)  "
          f"| 인당 주문 {rp['orders_per_buyer']}건")

    print("\n[5] 코호트 리텐션 (가입 주차 × N주 후 재구매, %)")
    cr = cohort_retention(od, data["users"])
    with pd.option_context("display.max_columns", None, "display.width", 120):
        print(cr.head(6).to_string(index=False))

    print("\n[6] 카테고리별 성과")
    cp = category_performance(od, data["products"])
    print(cp.to_string(index=False))

    print("\n[7] 상품 GMV TOP 5")
    pp = product_performance(ev, od, data["products"], top=5)
    print(pp.to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
