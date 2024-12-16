# Base stage
FROM node:18-alpine AS base

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Build stage for production
FROM base AS build


RUN npm run build

# production stage
FROM node:18-alpine AS production

WORKDIR /app

COPY --from=build /app /app

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]

# Development stage
FROM base AS dev

EXPOSE 3000

ENV NODE_ENV=development

CMD ["npm", "run", "dev"]
