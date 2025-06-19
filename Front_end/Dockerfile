# Stage 1: Build app
FROM node:18 as builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Xóa nội dung mặc định
RUN rm -rf /usr/share/nginx/html/*

# Copy file build vào nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy config nginx nếu có (hỗ trợ SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
