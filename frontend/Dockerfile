# Phase 2 Frontend Dockerfile

# Build stage
FROM node:18-alpine as build

WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치 (빌드에 필요한 dev 의존성 포함)
RUN npm install

# 소스 코드 복사
COPY . .

# 애플리케이션 빌드
RUN npm run build

# Production stage
FROM nginx:alpine

# Nginx 설정 복사
COPY nginx.prod.conf /etc/nginx/nginx.conf

# 빌드된 파일 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 포트 노출
EXPOSE 80

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
