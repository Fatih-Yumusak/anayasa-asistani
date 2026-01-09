# Frontend Dockerfile
FROM node:18-alpine

# Workdir
WORKDIR /app

# Dependency Install
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Start command
CMD ["npm", "start"]
