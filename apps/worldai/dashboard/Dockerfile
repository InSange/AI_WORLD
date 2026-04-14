FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# SPA 라우팅을 위한 기본 nginx 설정이 필요할 수 있음
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
