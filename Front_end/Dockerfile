FROM node:18-alpine

WORKDIR /app

# Copy and install dependencies
COPY package*.json ./
RUN npm install

# Copy all source files
COPY . .

# Build the Vite app
RUN npm run build

# Install 'serve' to serve static files
RUN npm install -g serve

# Expose the port for the server
EXPOSE 3006

# Serve the built app on all interfaces
CMD ["serve", "-s", "dist", "-l", "tcp://0.0.0.0:3006"]
