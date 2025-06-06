# -*- coding: utf-8 -*-
"""past_to_stroke.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1G-a0iTRQf9v5wjC0JOslNMc4071rp6Wq
"""

import cv2
import numpy as np
import os
import glob
import pandas as pd

# MRI 이미지 경로를 일련번호 기준으로 불러오는 함수
def load_mri_image_paths(folder_path):
    # 이미지 파일 경로를 모두 불러오기
    image_paths = glob.glob(os.path.join(folder_path, '*.png'))

    # 이미지 파일 이름에서 일련번호 추출하여 그룹화
    image_groups = {}
    for path in image_paths:
        # 파일 이름에서 일련번호 추출 (예: '1396028_8.png' -> '1396028')
        file_name = os.path.basename(path)
        serial_number = file_name.split('_')[0]

        # 일련번호를 키로, 해당 경로를 리스트로 저장
        if serial_number not in image_groups:
            image_groups[serial_number] = []
        image_groups[serial_number].append(path)

    return image_groups

# MRI 이미지에서 가장 밝은 점을 찾아 좌표 반환
def detect_brightest_features(image, max_features=5):
    # 이미지에서 가장 밝은 부분의 좌표를 찾는 방법
    # 가장 밝은 점들을 찾기 위해 이미지의 최대값과 위치를 찾음
    bright_coords = []

    # 이미지의 픽셀 값 중 가장 밝은 점을 여러 개 찾기 위해 max_features 만큼 반복
    for _ in range(max_features):
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
        bright_coords.append(max_loc)

        # 밝은 부분을 찾은 후 해당 부분을 마스크 처리하여 다시 찾지 않도록 함
        mask = np.zeros_like(image)
        cv2.circle(mask, max_loc, 5, 255, -1)  # 5 픽셀 반경으로 마스크
        image = cv2.bitwise_and(image, image, mask=~mask)  # 해당 부분을 제외한 이미지

    return bright_coords

# 33개의 MRI 이미지를 불러오는 함수 (이미지 파일 경로 리스트와 환자 ID 리스트 제공)
def load_mri_images(paths, patient_ids):
    patient_images = {}
    for patient_id, path in zip(patient_ids, paths):
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if patient_id in patient_images:
            patient_images[patient_id].append(image)
        else:
            patient_images[patient_id] = [image]
    return patient_images

# 뇌 부위를 판단하는 함수
def identify_brain_region(x, y, image_width, image_height):
    # 뇌 부위를 분할 (좌표 기준)
    if y < image_height * 0.3:
        return "전두엽"
    elif y >= image_height * 0.3 and y < image_height * 0.6:
        if x < image_width * 0.5:
            return "두정엽"
        else:
            return "측두엽"
    elif y >= image_height * 0.6:
        if x < image_width * 0.5:
            return "후두엽"
        else:
            return "소뇌"
    else:
        return "기저핵" if x < image_width * 0.5 else "뇌간"

# 각 이미지에서 가장 밝은 영역 좌표를 추출하고 뇌 부위를 식별하는 함수
def process_patient_images(patient_images):
    results = []

    for patient_id, images in patient_images.items():
        bright_regions = []

        for image in images:
            # 밝은 좌표 검출
            bright_coords = detect_brightest_features(image, max_features=5)
            for (x, y) in bright_coords:
                region = identify_brain_region(x, y, image.shape[1], image.shape[0])
                bright_regions.append(region)

        # 가장 많이 나온 뇌 부위로 뇌졸중 발생 부위 설정
        most_common_region = max(set(bright_regions), key=bright_regions.count)
        results.append({'일련번호': patient_id, '뇌졸중 발생 부위': most_common_region})

    return pd.DataFrame(results)

# MRI 이미지가 저장된 폴더 경로
folder_path = '/content/drive/MyDrive/Colab Notebooks/MRI'

# MRI 이미지 경로 불러오기
image_groups = load_mri_image_paths(folder_path)

# 일련번호와 해당 이미지 경로를 출력하여 확인
for serial, paths in image_groups.items():
    print(f"Serial number: {serial}, Image paths: {paths}")

# 이미지를 불러오고 환자별로 그룹화
# patient_ids는 일련번호를 그대로 사용
patient_ids = list(image_groups.keys())
image_paths = [path for paths in image_groups.values() for path in paths]

# MRI 이미지를 불러오고 환자별로 그룹화
patient_images = load_mri_images(image_paths, patient_ids)

# 각 환자의 뇌졸중 발생 부위 데이터 프레임 생성
df_stroke_regions = process_patient_images(patient_images)

# 결과 출력
print(df_stroke_regions)

# MRI 이미지가 저장된 폴더 경로
folder_path2 = '/content/drive/MyDrive/Colab Notebooks/MRI2'

# MRI 이미지 경로 불러오기
image_groups2 = load_mri_image_paths(folder_path2)

# 일련번호와 해당 이미지 경로를 출력하여 확인
for serial, paths in image_groups2.items():
    print(f"Serial number: {serial}, Image paths: {paths}")

# 이미지를 불러오고 환자별로 그룹화
# patient_ids는 일련번호를 그대로 사용
patient_ids2 = list(image_groups2.keys())
image_paths2 = [path for paths in image_groups2.values() for path in paths]

# MRI 이미지를 불러오고 환자별로 그룹화
patient_images2 = load_mri_images(image_paths2, patient_ids2)

# 각 환자의 뇌졸중 발생 부위 데이터 프레임 생성
df_stroke_regions2 = process_patient_images(patient_images2)

# 결과 출력
print(df_stroke_regions2)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 데이터 불러오기
nurse_data = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/5.간호정보조사지.csv")  # 간호 정보 데이터
diagnosis_data = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/2.환자진단_내역.csv")  # 환자 진단 내역 데이터
mri_metadata = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/metadata.csv")  # MRI 메타 데이터

# 2. column 정리
nurse_data = nurse_data[['일련번호', '체중', '신장', '고혈압', '당뇨']]
diagnosis_data = diagnosis_data[['일련번호', '성별', '진료_나이', '진단_질병_코드']]

# 3. 간호정보조사지와 환자진단내역 병합 (일련번호 기준)
# 일련번호의 데이터 타입을 일관성 있게 설정
nurse_data['일련번호'] = nurse_data['일련번호'].astype(int)
diagnosis_data['일련번호'] = diagnosis_data['일련번호'].astype(int)
df_stroke_regions['일련번호'] = df_stroke_regions['일련번호'].astype(int)
df_stroke_regions2['일련번호'] = df_stroke_regions2['일련번호'].astype(int)

# df_stroke_regions와 df_stroke_regions2를 하나로 결합
df_stroke_combined = pd.concat([df_stroke_regions, df_stroke_regions2], ignore_index=True)

merged_data = pd.merge(nurse_data, diagnosis_data, on='일련번호', how='left')
merged_data = pd.merge(merged_data, df_stroke_combined, on='일련번호', how='left')

# 4. 병합 후 데이터 확인
print("병합 후 데이터 확인:")
print(merged_data.head())
print(len(merged_data))

# 5. 결측값 처리
# 수치형 변수: 체중, 신장, 진료_나이
numeric_columns = ['체중', '신장', '진료_나이']
for col in numeric_columns:
    # 결측값은 중앙값으로 채움
    merged_data[col].fillna(merged_data[col].median(), inplace=True)

# 범주형 변수: 일련번호, 성별, 고혈압, 당뇨
categorical_columns = ['성별', '고혈압', '당뇨', '진단_질병_코드']
for col in categorical_columns:
    # 결측값은 최빈값으로 채움
    merged_data[col].fillna(merged_data[col].mode()[0], inplace=True)

# 6. 이상값 확인 (IQR 방법 사용)
outlier_rows = []  # 이상값 행을 기록할 리스트
for col in numeric_columns:
    Q1 = merged_data[col].quantile(0.25)
    Q3 = merged_data[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # 이상값 행을 표시하기 위해 outlier_rows에 추가
    outliers = merged_data[(merged_data[col] < lower_bound) | (merged_data[col] > upper_bound)]
    outlier_rows.append(outliers)

    # 이상값 시각화 (boxplot)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=merged_data, orient = 'v')
    plt.title(f"{col}의 이상값 확인")
    plt.show()

# 이상값이 포함된 행을 하나의 데이터프레임으로 결합
outlier_data = pd.concat(outlier_rows).drop_duplicates()
print("이상값이 있는 행:")
print(outlier_data)

# 이상값 행 제거
merged_data = merged_data[~merged_data.index.isin(outlier_data.index)]
len(merged_data)

# '뇌졸중 발생 부위' 값이 없는 행 제거
merged_data = merged_data[merged_data['뇌졸중 발생 부위'].notna()]

merged_data['stroke_type'] = merged_data['진단_질병_코드'].apply(lambda x: 1 if 'I63' in str(x) else 0)
merged_data['고혈압'] = merged_data['고혈압'].apply(lambda x: 1 if 'Y' in str(x) else 0)
merged_data['당뇨'] = merged_data['당뇨'].apply(lambda x: 1 if 'Y' in str(x) else 0)
merged_data['성별'] = merged_data['성별'].apply(lambda x: 1 if 'M' in str(x) else 0)
merged_data = merged_data.drop_duplicates(subset=['일련번호'])
# 뇌졸중 발생 부위 매핑 사전 생성
stroke_region_mapping = {
    '전두엽': 1,
    '후두엽': 2,
    '측두엽': 3,
    '두정엽': 4,
    '소뇌': 5
}

# map() 함수를 사용하여 매핑 적용
# '뇌졸중 발생 부위' 열을 문자열로 변환하고 공백 제거 후 매핑 적용
merged_data['뇌졸중 발생 부위'] = (
    merged_data['뇌졸중 발생 부위'].astype(str).str.strip().map(stroke_region_mapping).fillna(0).astype(int)
)

len(merged_data)
merged_data.head()

# 10. 데이터 분리 (7:3 비율로 학습 데이터와 테스트 데이터 분리)
X = merged_data.drop(columns=['stroke_type', '일련번호', '진단_질병_코드', '뇌졸중 발생 부위'])  # 특성들 (일련번호, 라벨 제외)
y = merged_data['뇌졸중 발생 부위']  # 라벨 (stroke_location)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 11. 모델 학습 (랜덤 포레스트 모델)
model = RandomForestClassifier(n_estimators=1000, max_depth=10, min_samples_split=7)
model.fit(X_train, y_train)

# 모델 평가
y_pred = model.predict(X_test)
print("모델 평가 결과:")
print(classification_report(y_test, y_pred))  # average 인자 제거
print("Accuracy: ", accuracy_score(y_test, y_pred))

from sklearn.metrics import classification_report, accuracy_score

# 예측 결과를 텍스트로 변환 (숫자 -> 텍스트)
region_mapping_reverse = {v: k for k, v in stroke_region_mapping.items()}  # 숫자 -> 텍스트 매핑

# 모델 예측 값과 실제 값 텍스트로 변환
y_pred_text = [region_mapping_reverse.get(x, 'Unknown') for x in y_pred]
y_test_text = [region_mapping_reverse.get(x, 'Unknown') for x in y_test]

# 모델 평가 결과 출력
print("모델 평가 결과:")
print(classification_report(y_test_text, y_pred_text))  # 텍스트로 평가
print("Accuracy: ", accuracy_score(y_test_text, y_pred_text))

from sklearn.model_selection import cross_val_score

# 교차 검증을 통해 정확도 평가 (예: 5-fold 교차 검증)
cv_scores = cross_val_score(RandomForestClassifier(), X_train, y_train, cv=5, scoring='accuracy')

print(cv_scores)

# 13. 중요 변수 출력
feature_importance = model.feature_importances_
ranking = np.argsort(feature_importance)[::-1]  # 중요도가 높은 변수 순으로 정렬

print("변수 중요도:")
for i in range(X_train.shape[1]):
    print(f"{X_train.columns[ranking[i]]}: {feature_importance[ranking[i]]}")

# 14. 모델 시각화 (변수 중요도 시각화)
plt.figure(figsize=(10, 6))
sns.barplot(x=feature_importance[ranking], y=X_train.columns[ranking])
plt.title("Feature Importance")
plt.xlabel("Importance")
plt.ylabel("Features")
plt.show()

from google.colab import drive
drive.mount('/content/drive')