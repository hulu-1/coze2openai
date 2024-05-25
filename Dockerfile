# 使用轻量级的 Node.js 14 LTS 版本基于 Alpine 的 Docker 镜像
FROM node:14-alpine3.12

# 设置工作目录
WORKDIR /app

# 从当前 Docker 客户端位置COPY package.json 和 package-lock.json
COPY package.json package-lock.json ./

# 安装 app 依赖项 - npm@latest 已经包含在 Node.js 14 LTS 中
RUN npm install

# 如果您的项目包含需要编译的原生依赖项，则需要确认 Alpine 镜像中的
# 安装工具都安装完毕。常见的情况包括安装 gcc、make 等。
# RUN apk update && apk add --no-cache gcc g++ make

# 默认情况下，如果你有静态文件或编译后的资源，请复制到工作目录
COPY . .

# CMD 指定 Docker 容器启动时要运行的命令
CMD ["npm", "start"]
