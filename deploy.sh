#!/bin/bash

# 변수 설정
IMAGE_NAME="yeseul01/ocr-api:latest"
DEPLOYMENT_NAME="ocr-api"

echo " 1. SpringBoot 이미지 빌드 중..."
docker build -t $IMAGE_NAME .

echo " 2. DockerHub에 이미지 푸시 중..."
docker push $IMAGE_NAME

echo " 3. Kubernetes Deployment 재시작 중..."
kubectl rollout restart deployment $DEPLOYMENT_NAME

echo "4. 현재 Pod 상태 확인 중..."
kubectl get pods -l app=$DEPLOYMENT_NAME

echo "웹에서 테스트 "
