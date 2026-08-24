import glob
import os
import pandas as pd

def load_opinosis_data(path: str) -> pd.DataFrame:
    """
    UCI Opinosis 데이터셋 폴더를 순회하며 개별 리뷰 단위로 데이터프레임을 생성합니다.
    """
    all_files = glob.glob(os.path.join(path, "*.data"))
    
    filename_list = []
    opinion_text_list = []

    for file_ in all_files:
        try:
            df = pd.read_table(file_, index_col=None, header=None, encoding='latin1', names=['review'])
        except Exception:
            df = pd.read_table(file_, index_col=None, header=0, encoding='latin1')
            if 'review' not in df.columns:
                df.columns = ['review']

        filename_ = os.path.basename(file_)
        filename = os.path.splitext(filename_)[0]

        for review in df['review'].dropna():
            filename_list.append(filename)
            opinion_text_list.append(str(review).strip())

    document_df = pd.DataFrame({
        'topic': filename_list, 
        'review': opinion_text_list
    })
    
    return document_df