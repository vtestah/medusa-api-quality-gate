FROM node:24-alpine

WORKDIR /server

ENV NPM_CONFIG_UPDATE_NOTIFIER=false
ENV NPM_CONFIG_FUND=false

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./

RUN pnpm install --frozen-lockfile

COPY . .

RUN chmod +x start.sh

EXPOSE 9000
EXPOSE 5173

CMD ["./start.sh"]
