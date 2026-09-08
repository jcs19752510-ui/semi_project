"""문서 군집화(업무명=03. 문서 군집화) 도메인.

근거 노트북: 정찬성/ipynb/src/07_문서군집화_실습_RandomForest추가.ipynb
원본 흐름:
  1) Opinosis 리뷰 문서 51건(파일명 예: bathroom_bestwestern_hotel_sfo.txt.data)을 읽어
     TF-IDF로 벡터화(영어 불용어 제거 + 1~2-gram)
  2) KMeans로 비지도 군집화(문서 간 유사도 기반 그룹핑 — 정답 라벨 없음)
  3) 파일명 접두어(예: 'bathroom')를 "정답 카테고리"로 뽑아, RandomForest로 "TF-IDF만으로
     카테고리를 얼마나 잘 맞히는지" 보조 검증(카테고리 1건뿐인 클래스는 계층화 분할이 안 되므로
     노트북 자체가 카테고리당 2건 이상인 표본만 걸러 StratifiedKFold로 평가)

이 모듈은 위 흐름을 그대로 따르되, RandomForest 한 종류가 아니라 registry의 5종 분류기
카탈로그(로지스틱회귀/LightGBM/XGBoost/랜덤포레스트/GradientBoost) 전부를 동일한 방식으로
평가할 수 있게 일반화했다 — 산탄데르/신용카드 업무와 같은 "업무명→모델명 선택" UX를 그대로
쓰기 위함(§가이드요청서 신규 요청: "5개의 모델을 화면에서 조회").

주요 설계 결정:
- NLTK 표제어(lemmatization)는 배포 환경에서 코퍼스(wordnet/punkt)를 내려받아야 하는 런타임
  의존성이라(콜드스타트/네트워크 실패 재발 우려, §운영오류 교훈) 쓰지 않는다. sklearn
  TfidfVectorizer 기본 토크나이저 + 영어 불용어 제거만 적용한다 — 군집 품질보다 배포
  안정성을 우선한 절충이며, 실측(§내부테스트 결과서)으로 유의미한 군집/분류 결과가 나옴을
  확인했다.
- 타깃이 이진(0/1)이 아니라 다중클래스(카테고리 최대 36종)이므로, 모델 수행결과는
  단순 ROC가 아니라 표준 sklearn 레시피인 "macro One-vs-Rest 평균 ROC 곡선"으로 계산한다.
  이렇게 하면 기존 ModelResultResponse({curves:[{model,label,auc,fpr,tpr}]}) 스키마와
  프론트 ROC 차트를 그대로 재사용할 수 있다(전처리검증 4종 차트는 이진 스키마와 의미가
  근본적으로 달라 DocClusteringPreprocessResponse를 별도로 둔 것과 대비된다).
"""

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import label_binarize

from app.core.config import get_settings
from app.domains.dataviz import crud, ml

# 노트북은 5개 군집과 3개 군집 두 가지를 다 실험했다. 3개 군집 쪽이 노트북의 최종
# cross-tab 분석(§셀 16)에 쓰인 값이라 대시보드도 이를 채택한다 — boxplot 그룹 수도
# 3개면 화면에서 비교하기 알맞다(카테고리 36종을 그대로 그룹으로 쓰면 boxplot이 무의미해짐).
N_CLUSTERS = 3

MODEL_LABELS = ml.MODEL_LABELS
CURVE_POINTS = ml.CURVE_POINTS

# TfidfVectorizer(min_df=0.05)는 원본 노트북 값(비율 기준)이지만, 대시보드는 테스트에서
# 문서 수가 훨씬 적은 표본을 주입하는 경우가 있어(§conftest) 비율 기준 min_df는 표본 크기에
# 따라 의미가 흔들린다. 정수(문서 2건 이상에 등장)로 고정해 "최소 2개 문서에 공통으로
# 나타나는 단어만 피처로 쓴다"는 동일한 취지를 표본 크기와 무관하게 유지한다.
TFIDF_MIN_DF = 2
TFIDF_MAX_DF = 0.85


def _read_corpus(topics_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for path in sorted(topics_dir.glob("*.data")):
        text = path.read_text(encoding="latin1")
        filename = path.name.split(".")[0]
        # 예: 'bathroom_bestwestern_hotel_sfo' -> 카테고리 'bathroom'
        # (battery-life처럼 카테고리 자체에 '_'가 없는 경우만 전제 — 원본 노트북과 동일 규칙)
        category = filename.split("_")[0]
        rows.append({"filename": filename, "category": category, "opinion_text": text})
    return pd.DataFrame(rows)


def _vectorize_and_cluster(document_df: pd.DataFrame) -> tuple[pd.DataFrame, csr_matrix]:
    document_df = document_df.copy()
    document_df["word_count"] = document_df["opinion_text"].str.split().str.len()

    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), min_df=TFIDF_MIN_DF, max_df=TFIDF_MAX_DF
    )
    feature_matrix = vectorizer.fit_transform(document_df["opinion_text"])

    n_clusters = min(N_CLUSTERS, len(document_df)) or 1
    km = KMeans(n_clusters=n_clusters, max_iter=10000, n_init=10, random_state=0)
    document_df["cluster_label"] = km.fit_predict(feature_matrix)

    return document_df, feature_matrix


@lru_cache
def _load_document_corpus() -> tuple[pd.DataFrame, csr_matrix]:
    settings = get_settings()
    document_df = _read_corpus(Path(settings.doc_clustering_topics_dir))
    return _vectorize_and_cluster(document_df)


def get_document_corpus() -> tuple[pd.DataFrame, csr_matrix]:
    """FastAPI 진입점. 테스트에서는 이 함수를 override해 작은 표본으로 대체한다."""
    return _load_document_corpus()


# ── 전처리 데이터 검증결과 4종 ──────────────────────────────────────────────


def _category_distribution(df: pd.DataFrame) -> dict:
    counts = df["category"].value_counts().sort_index()
    return {"labels": counts.index.tolist(), "counts": [int(c) for c in counts.to_numpy()]}


def _length_bins(df: pd.DataFrame, bins: int = 5) -> list[dict]:
    if len(df) == 0:
        return []
    try:
        binned = pd.qcut(df["word_count"], q=bins, duplicates="drop")
    except ValueError:
        # 표본이 작아 분위 개수만큼 값이 나뉘지 않는 경우(단위 테스트 등) 단일 구간으로 대체.
        binned = pd.cut(df["word_count"], bins=1)

    result: list[dict] = []
    for interval, group in df.groupby(binned, observed=True)["word_count"]:
        if len(group) == 0:
            continue
        result.append({"range": str(interval), "count": int(len(group))})
    return result


def _cluster_distribution(df: pd.DataFrame) -> dict:
    counts = df["cluster_label"].value_counts().sort_index()
    return {
        "labels": [f"클러스터 {c}" for c in counts.index.tolist()],
        "counts": [int(c) for c in counts.to_numpy()],
    }


def _length_boxplot(df: pd.DataFrame) -> list[dict]:
    result: list[dict] = []
    for cluster_id in sorted(df["cluster_label"].unique()):
        summary = crud.five_number_summary(df.loc[df["cluster_label"] == cluster_id, "word_count"])
        result.append({"group": f"클러스터 {cluster_id}", "summary": summary})
    return result


def run_preprocess_check(document_df: pd.DataFrame) -> dict:
    return {
        "category_distribution": _category_distribution(document_df),
        "length_bins": _length_bins(document_df),
        "cluster_distribution": _cluster_distribution(document_df),
        "length_boxplot": _length_boxplot(document_df),
        "labels": {
            "category_title": "카테고리별 문서 수 분포",
            "length_title": "문서 길이(단어 수) 구간별 문서 수",
            "cluster_title": f"K-Means 군집별 문서 수 (k={N_CLUSTERS})",
            "boxplot_title": "군집별 문서 길이(단어 수) 비교",
        },
    }


# ── 모델 수행결과: 카테고리(다중클래스) 분류기 macro OvR ROC ───────────────────


def _flat_curve(model: str) -> dict:
    return {
        "model": model,
        "label": MODEL_LABELS.get(model, model),
        "auc": 0.5,
        "fpr": [0.0, 1.0],
        "tpr": [0.0, 1.0],
    }


def _train_and_evaluate(document_df: pd.DataFrame, feature_matrix: csr_matrix, model: str) -> dict:
    # (A)~(C) 원본 노트북과 동일한 가드: 카테고리(정답 라벨)가 1건뿐이면 계층화 분할이
    # 불가능하므로 평가 대상에서 제외한다.
    category_counts = document_df["category"].value_counts()
    valid_categories = category_counts[category_counts >= 2].index
    mask = document_df["category"].isin(valid_categories).to_numpy()

    y_eval = document_df.loc[mask, "category"].reset_index(drop=True)
    n_classes = int(y_eval.nunique())
    min_class_count = int(y_eval.value_counts().min()) if n_classes else 0

    if n_classes < 2 or min_class_count < 2:
        # 유효 표본이 너무 적어 교차검증 자체가 불가능한 경우 — ml.py의 소표본 degrade
        # 패턴과 동일하게 임의 확률(0.5)로 대체한 평평한 곡선을 반환한다.
        return _flat_curve(model)

    # GradientBoostingClassifier 등 일부 분류기의 sparse 입력 지원이 sklearn 버전마다
    # 갈려(§검증스크립트로 사전 확인) 다섯 모델 모두 동일하게 dense로 변환한다.
    # 문서 51건 규모(피처 최대 1만여 개)에서는 메모리 부담이 미미하다.
    X_eval = np.asarray(feature_matrix[mask].todense())

    classes = np.sort(y_eval.unique())
    n_splits = min(5, min_class_count)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    clf = ml.build_classifier(model)
    # 51건 남짓의 극소표본에서는 단일 홀드아웃(70/30)보다 StratifiedKFold 교차검증의
    # out-of-fold 예측확률을 쓰는 쪽이 통계적으로 더 신뢰할 수 있다(원본 노트북 §셀14 채택).
    proba = cross_val_predict(clf, X_eval, y_eval, cv=skf, method="predict_proba")

    y_bin = label_binarize(y_eval, classes=classes)
    auc = float(roc_auc_score(y_bin, proba, average="macro"))

    # sklearn 표준 다중클래스 macro-average ROC 레시피: 클래스별 One-vs-Rest ROC를
    # 공통 FPR 그리드에 보간(interp)한 뒤 평균낸다.
    all_fpr = np.unique(
        np.concatenate([roc_curve(y_bin[:, i], proba[:, i])[0] for i in range(len(classes))])
    )
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(len(classes)):
        fpr_i, tpr_i, _ = roc_curve(y_bin[:, i], proba[:, i])
        mean_tpr += np.interp(all_fpr, fpr_i, tpr_i)
    mean_tpr /= len(classes)

    fpr_list, tpr_list = ml.downsample_curve(all_fpr, mean_tpr, CURVE_POINTS)
    return {
        "model": model,
        "label": MODEL_LABELS.get(model, model),
        "auc": round(auc, 4),
        "fpr": [round(v, 4) for v in fpr_list],
        "tpr": [round(v, 4) for v in tpr_list],
    }


# ml.compute_roc_curve와 동일한 수동 캐시 패턴: (데이터 객체 id, model) 조합으로 캐싱해
# 요청마다 재학습하지 않는다.
_cache: dict[tuple[int, str], dict] = {}


def compute_model_result(document_df: pd.DataFrame, feature_matrix: csr_matrix, model: str) -> dict:
    key = (id(document_df), model)
    if key not in _cache:
        _cache[key] = _train_and_evaluate(document_df, feature_matrix, model)
    return _cache[key]
