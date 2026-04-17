#!/bin/sh

set -eu

pnpm exec medusa db:migrate

exec pnpm dev
