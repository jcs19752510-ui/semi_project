from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from imblearn.over_sampling import SMOTE

def train_baseline(X_train, y_train):
    """08단계: Baseline (Dummy Classifier)"""
    dummy = DummyClassifier(strategy='stratified', random_state=42)
    dummy.fit(X_train, y_train)
    return dummy

def train_logistic_regression(X_train, y_train, class_weight=None):
    """09단계 & 11단계: 로지스틱 회귀 (Class Weight 적용 가능)"""
    lr = LogisticRegression(max_iter=1000, class_weight=class_weight, random_state=42)
    lr.fit(X_train, y_train)
    return lr

def train_random_forest(X_train, y_train, class_weight=None):
    """10~11단계: Random Forest"""
    rf = RandomForestClassifier(n_estimators=100, class_weight=class_weight, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    return rf

def train_xgboost(X_train, y_train, scale_pos_weight=1):
    """10~11단계: XGBoost (불균형 조절을 위해 scale_pos_weight 활용 가능)"""
    xgb = XGBClassifier(scale_pos_weight=scale_pos_weight, random_state=42, n_jobs=-1, eval_metric='logloss')
    xgb.fit(X_train, y_train)
    return xgb

def apply_smote(X_train, y_train):
    """11단계: SMOTE 오버샘플링"""
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    return X_resampled, y_resampled