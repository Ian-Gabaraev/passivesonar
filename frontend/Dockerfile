# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install the app dependencies
RUN npm install

# Copy the rest of the app's source code
COPY . .

# Build the React app
RUN npm run build

# Install a simple HTTP server to serve static content
RUN npm install -g serve

# Set the command to run the app
CMD ["serve", "-s", "build"]

# Expose the port the app runs on
EXPOSE 3000
