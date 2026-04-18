#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

POSTGRES_DB_NAME="${POSTGRES_DB:-medusa}"
POSTGRES_USER_NAME="${POSTGRES_USER:-postgres}"

PUBLISHABLE_KEY="$(
  docker compose exec -T postgres \
    psql -U "$POSTGRES_USER_NAME" -d "$POSTGRES_DB_NAME" -At \
    -c "select token from api_key where type = 'publishable' limit 1;"
)"

if [[ -z "$PUBLISHABLE_KEY" ]]; then
  echo "No publishable key found in Medusa database." >&2
  exit 1
fi

update_env_file() {
  local file_path="$1"
  local variable_name="$2"

  if [[ ! -f "$file_path" ]]; then
    return
  fi

  if rg -q "^${variable_name}=" "$file_path"; then
    sed -i "s|^${variable_name}=.*|${variable_name}=${PUBLISHABLE_KEY}|" "$file_path"
    return
  fi

  printf "\n%s=%s\n" "$variable_name" "$PUBLISHABLE_KEY" >> "$file_path"
}

update_env_file ".env" "STOREFRONT_MEDUSA_PUBLISHABLE_KEY"
update_env_file "apps/storefront/.env.local" "NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY"

printf "Synced Medusa publishable key: %s\n" "$PUBLISHABLE_KEY"
