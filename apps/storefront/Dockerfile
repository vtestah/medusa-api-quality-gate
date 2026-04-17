FROM node:24-alpine

WORKDIR /workspace

ENV NPM_CONFIG_UPDATE_NOTIFIER=false
ENV NPM_CONFIG_FUND=false

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/storefront/package.json apps/storefront/package.json

RUN pnpm install --filter ./apps/storefront... --frozen-lockfile

COPY apps/storefront ./apps/storefront

RUN chmod +x ./apps/storefront/start.sh

EXPOSE 8000

CMD ["./apps/storefront/start.sh"]
