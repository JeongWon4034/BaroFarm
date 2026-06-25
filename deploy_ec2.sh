#!/bin/bash
# EC2 초기 세팅 스크립트 (Amazon Linux 2023 또는 Ubuntu 22.04)
# 사용법: EC2에 SSH 접속 후 실행
#   curl -sSL https://raw.githubusercontent.com/.../deploy_ec2.sh | bash
# 또는 파일 업로드 후: chmod +x deploy_ec2.sh && ./deploy_ec2.sh

set -e

# ── 1. Docker 설치 ────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "[1/4] Docker 설치 중..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  sudo systemctl enable --now docker
else
  echo "[1/4] Docker 이미 설치됨"
fi

if ! command -v docker compose &>/dev/null 2>&1; then
  echo "      Docker Compose 플러그인 설치..."
  sudo apt-get install -y docker-compose-plugin 2>/dev/null || \
    sudo yum install -y docker-compose-plugin 2>/dev/null || true
fi

# ── 2. 코드 클론 ─────────────────────────────────────────
echo "[2/4] 코드 클론..."
if [ ! -d "15pjt_lees" ]; then
  git clone https://github.com/<YOUR_ORG>/15pjt_lees.git
fi
cd 15pjt_lees

# ── 3. EC2 퍼블릭 IP 자동 감지 ──────────────────────────
EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "[3/4] EC2 IP: $EC2_PUBLIC_IP"
export EC2_PUBLIC_IP

# ── 4. 빌드 & 실행 ───────────────────────────────────────
echo "[4/4] Docker 빌드 & 실행..."
docker compose -f docker-compose.aws.yml up -d --build

echo ""
echo "======================================"
echo " 배포 완료!"
echo " 대시보드: http://$EC2_PUBLIC_IP:3001"
echo " 백엔드:   http://$EC2_PUBLIC_IP:8000"
echo "======================================"
