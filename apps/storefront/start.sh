#!/bin/sh

set -eu

pnpm install --filter ./apps/storefront... --frozen-lockfile

cd /workspace/apps/storefront

exec pnpm dev
