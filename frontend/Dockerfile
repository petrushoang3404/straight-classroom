FROM node:22-alpine AS build

RUN corepack enable && corepack prepare yarn@4 --activate
WORKDIR /app

COPY package.json yarn.lock .yarnrc.yml ./
RUN yarn install --immutable

COPY . .
# Requests go to the same origin under /api (see nginx.conf), which is the
# client's default base URL, so nothing needs configuring at build time.
RUN yarn build


FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
