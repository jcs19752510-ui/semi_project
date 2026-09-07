"""
Mercari Price Suggestion Challenge - 전체 파이프라인
(03_회귀/1.ipynb 와 동일한 로직을 스크립트로 실행하여 결과를 results/ 에 저장)

참고: https://medium.com/@shivdutta/mercari-price-suggestion-challenge-a-deep-learning-regression-case-study-985ef2e560d
"""
import os
import time
import pickle

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import hstack
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
import lightgbm as lgb
from wordcloud import WordCloud

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'mercari_train.tsv')
RESULT_DIR = os.path.join(BASE_DIR, 'results')
FIG_DIR = os.path.join(RESULT_DIR, 'figures')
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_style('whitegrid')


def save_pickle(obj, name):
    path = os.path.join(RESULT_DIR, f'{name}.pkl')
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    print(f'[saved pickle] {path}', flush=True)


def savefig(name):
    path = os.path.join(FIG_DIR, f'{name}.png')
    plt.tight_layout()
    plt.savefig(path, dpi=110)
    plt.close()
    print(f'[saved figure] {path}', flush=True)


def rmsle(y_true_log, y_pred_log):
    # y가 이미 log1p 스케일이면 RMSE == RMSLE
    return np.sqrt(mean_squared_error(y_true_log, y_pred_log))


def split_category(cat):
    if pd.isnull(cat):
        return ['Other_Null', 'Other_Null', 'Other_Null']
    parts = cat.split('/')
    parts = parts + ['Other_Null'] * (3 - len(parts))
    return parts[:3]


def main():
    t_start = time.time()

    # ---------- 1. 데이터 로드 ----------
    print('1) 데이터 로드', flush=True)
    mercari_df = pd.read_csv(DATA_PATH, sep='\t')
    print('data shape:', mercari_df.shape, flush=True)

    # ---------- 2. 결측치 확인 (전처리 전) ----------
    print('2) 결측치 확인 (전)', flush=True)
    missing_before = mercari_df.isnull().sum()
    no_desc_literal = int((mercari_df['item_description'] == 'No description yet').sum())
    print(missing_before, flush=True)
    print('item_description == "No description yet" (literal):', no_desc_literal, flush=True)

    plt.figure(figsize=(8, 4))
    missing_before[missing_before > 0].plot(kind='bar', color='#4C72B0')
    plt.title('Missing value count (before preprocessing)')
    plt.ylabel('missing count')
    savefig('01_missing_before')
    save_pickle({'missing_before': missing_before, 'no_desc_literal_before': no_desc_literal}, 'missing_before')

    # ---------- 3. price 분포 (로그변환 전/후 비교) ----------
    print('3) price 분포 전/후 비교', flush=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(mercari_df['price'], bins=100, ax=axes[0], color='#4C72B0')
    axes[0].set_title('Price distribution (raw)')
    axes[0].set_xlabel('price ($)')

    mercari_df['log_price'] = np.log1p(mercari_df['price'])
    sns.histplot(mercari_df['log_price'], bins=100, ax=axes[1], color='#DD8452')
    axes[1].set_title('Price distribution (log1p transformed)')
    axes[1].set_xlabel('log1p(price)')
    savefig('02_price_distribution_before_after')

    price_skew = float(mercari_df['price'].skew())
    log_price_skew = float(mercari_df['log_price'].skew())
    print('price skew:', price_skew, '-> log_price skew:', log_price_skew, flush=True)

    # ---------- 4. EDA ----------
    print('4) EDA', flush=True)
    plt.figure(figsize=(6, 4))
    sns.boxplot(data=mercari_df, x='item_condition_id', y='log_price')
    plt.title('log(price) by item_condition_id')
    savefig('03_condition_boxplot')

    plt.figure(figsize=(6, 4))
    for ship_val, label in [(1, 'seller pays'), (0, 'buyer pays')]:
        subset = mercari_df.loc[mercari_df['shipping'] == ship_val, 'log_price']
        sns.ecdfplot(subset, label=label)
    plt.legend()
    plt.title('CDF of log(price) by shipping payer')
    savefig('04_shipping_cdf')

    cats = mercari_df['category_name'].apply(split_category)
    mercari_df['category_main'] = cats.apply(lambda x: x[0])
    mercari_df['category_sub1'] = cats.apply(lambda x: x[1])
    mercari_df['category_sub2'] = cats.apply(lambda x: x[2])

    plt.figure(figsize=(8, 5))
    mercari_df['category_main'].value_counts().plot(kind='barh', color='#55A868')
    plt.title('Item count by main category')
    plt.gca().invert_yaxis()
    savefig('05_category_main_count')

    plt.figure(figsize=(8, 5))
    mercari_df['brand_name'].value_counts().head(10).plot(kind='barh', color='#C44E52')
    plt.title('Top 10 brands by item count')
    plt.gca().invert_yaxis()
    savefig('06_brand_top10')

    sample_n = min(200000, len(mercari_df))
    text_for_wc = ' '.join(
        mercari_df['name'].dropna().sample(sample_n, random_state=42).astype(str)
    )
    wc = WordCloud(width=900, height=450, background_color='white').generate(text_for_wc)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('WordCloud - name')
    savefig('07_wordcloud_name')

    # ---------- 5. 결측치 처리 (전처리) ----------
    print('5) 결측치 처리', flush=True)
    mercari_df['brand_name'] = mercari_df['brand_name'].fillna('Other_Null')
    mercari_df['category_main'] = mercari_df['category_main'].fillna('Other_Null')
    mercari_df['category_sub1'] = mercari_df['category_sub1'].fillna('Other_Null')
    mercari_df['category_sub2'] = mercari_df['category_sub2'].fillna('Other_Null')
    mercari_df['item_description'] = mercari_df['item_description'].fillna('No description yet')

    check_cols = ['brand_name', 'category_main', 'category_sub1', 'category_sub2', 'item_description']
    missing_after = mercari_df[check_cols].isnull().sum()
    plt.figure(figsize=(8, 4))
    missing_after.plot(kind='bar', color='#55A868')
    plt.title('Missing value count (after preprocessing)')
    plt.ylabel('missing count')
    plt.ylim(0, max(1, int(missing_before.max())))
    savefig('08_missing_after')
    save_pickle(missing_after, 'missing_after')

    save_pickle(mercari_df, 'mercari_df_preprocessed')

    # ---------- 6. 텍스트 결합 / 길이 피처 ----------
    print('6) 텍스트 결합/길이 피처', flush=True)
    mercari_df['text'] = mercari_df['name'].fillna('') + ' ' + mercari_df['item_description'].fillna('')
    mercari_df['text_len'] = mercari_df['text'].str.len()

    plt.figure(figsize=(6, 4))
    sample_plot = mercari_df.sample(min(50000, len(mercari_df)), random_state=42)
    sns.scatterplot(data=sample_plot, x='text_len', y='log_price', alpha=0.2, s=8)
    plt.title('text length vs log(price) (sample 50k)')
    savefig('09_textlen_vs_logprice')

    # ---------- 7. 피처 벡터화 ----------
    print('7) 피처 벡터화', flush=True)
    t_vec = time.time()
    cnt_vec_name = CountVectorizer()
    X_name = cnt_vec_name.fit_transform(mercari_df['name'])
    print('X_name shape:', X_name.shape, flush=True)

    tfidf_vec_descp = TfidfVectorizer(max_features=50000, ngram_range=(1, 3), stop_words='english')
    X_descp = tfidf_vec_descp.fit_transform(mercari_df['item_description'])
    print('X_descp shape:', X_descp.shape, flush=True)

    lb_brand_name = LabelBinarizer(sparse_output=True)
    X_brand = lb_brand_name.fit_transform(mercari_df['brand_name'])

    lb_category_main = LabelBinarizer(sparse_output=True)
    X_category_main = lb_category_main.fit_transform(mercari_df['category_main'])

    lb_category_sub1 = LabelBinarizer(sparse_output=True)
    X_category_sub1 = lb_category_sub1.fit_transform(mercari_df['category_sub1'])

    lb_category_sub2 = LabelBinarizer(sparse_output=True)
    X_category_sub2 = lb_category_sub2.fit_transform(mercari_df['category_sub2'])

    lb_item_cond_id = LabelBinarizer(sparse_output=True)
    X_item_cond_id = lb_item_cond_id.fit_transform(mercari_df['item_condition_id'])

    lb_shipping = LabelBinarizer(sparse_output=True)
    X_shipping = lb_shipping.fit_transform(mercari_df['shipping'])

    X_features_sparse = hstack([
        X_name, X_descp, X_brand, X_category_main, X_category_sub1,
        X_category_sub2, X_item_cond_id, X_shipping
    ]).tocsr()
    print('X_features_sparse shape:', X_features_sparse.shape, flush=True)
    print('벡터화 소요 시간(초):', time.time() - t_vec, flush=True)

    save_pickle(X_features_sparse, 'X_features_sparse')
    save_pickle({
        'cnt_vec_name': cnt_vec_name,
        'tfidf_vec_descp': tfidf_vec_descp,
        'lb_brand_name': lb_brand_name,
        'lb_category_main': lb_category_main,
        'lb_category_sub1': lb_category_sub1,
        'lb_category_sub2': lb_category_sub2,
        'lb_item_cond_id': lb_item_cond_id,
        'lb_shipping': lb_shipping,
    }, 'vectorizers')

    # ---------- 8. train/test split ----------
    print('8) train/test split', flush=True)
    y_target = mercari_df['log_price']
    X_train, X_test, y_train, y_test = train_test_split(
        X_features_sparse, y_target, test_size=0.2, random_state=156
    )
    save_pickle((y_test.index), 'test_index')

    # ---------- 9. Ridge 베이스라인 ----------
    print('9) Ridge 학습', flush=True)
    t_ridge = time.time()
    ridge_model = Ridge(solver='lsqr', fit_intercept=False, alpha=3)
    ridge_model.fit(X_train, y_train)
    ridge_pred = ridge_model.predict(X_test)
    ridge_rmsle = rmsle(y_test, ridge_pred)
    ridge_time = time.time() - t_ridge
    print(f'Ridge RMSLE: {ridge_rmsle:.5f}  (학습시간 {ridge_time:.1f}s)', flush=True)
    save_pickle(ridge_model, 'ridge_model')
    save_pickle(ridge_pred, 'ridge_pred')

    # ---------- 10. LightGBM ----------
    print('10) LightGBM 학습', flush=True)
    t_lgbm = time.time()
    lgbm_model = lgb.LGBMRegressor(
        n_estimators=200, learning_rate=0.1, num_leaves=125,
        n_jobs=-1, random_state=156
    )
    lgbm_model.fit(X_train, y_train)
    lgbm_pred = lgbm_model.predict(X_test)
    lgbm_rmsle = rmsle(y_test, lgbm_pred)
    lgbm_time = time.time() - t_lgbm
    print(f'LightGBM RMSLE: {lgbm_rmsle:.5f}  (학습시간 {lgbm_time:.1f}s)', flush=True)
    save_pickle(lgbm_model, 'lgbm_model')
    save_pickle(lgbm_pred, 'lgbm_pred')

    # ---------- 11. 모델 비교 시각화 ----------
    print('11) 모델 비교 시각화', flush=True)
    plt.figure(figsize=(5, 4))
    plt.bar(['Ridge', 'LightGBM'], [ridge_rmsle, lgbm_rmsle], color=['#4C72B0', '#DD8452'])
    plt.ylabel('RMSLE (lower is better)')
    plt.title('Model RMSLE comparison')
    savefig('10_model_rmsle_comparison')

    # ---------- 12. 결과 요약 저장 ----------
    results_summary = {
        'data_shape': mercari_df.shape,
        'price_skew_before': price_skew,
        'price_skew_after_log': log_price_skew,
        'no_desc_literal_before': no_desc_literal,
        'X_features_sparse_shape': X_features_sparse.shape,
        'X_name_shape': X_name.shape,
        'X_descp_shape': X_descp.shape,
        'n_brand_classes': len(lb_brand_name.classes_),
        'n_category_main_classes': len(lb_category_main.classes_),
        'ridge_rmsle': float(ridge_rmsle),
        'ridge_train_time_sec': ridge_time,
        'lgbm_rmsle': float(lgbm_rmsle),
        'lgbm_train_time_sec': lgbm_time,
        'total_time_sec': time.time() - t_start,
    }
    save_pickle(results_summary, 'results_summary')
    print('=== DONE ===', flush=True)
    print(results_summary, flush=True)


if __name__ == '__main__':
    main()