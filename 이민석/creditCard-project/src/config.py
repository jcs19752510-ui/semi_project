import os

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw', 'creditcard.csv')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
FIGURE_DIR = os.path.join(OUTPUT_DIR, 'figures')
MODEL_DIR = os.path.join(OUTPUT_DIR, 'models')

# 모델 학습 설정
RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET_COL = 'Class'