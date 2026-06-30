import http from "k6/http";
import { check, sleep } from "k6";

// Load profile: ramp a modest number of virtual users against the read-only
// Store API endpoints the storefront depends on. A baseline to watch error rate
// and latency under sustained traffic, not a stress test. See k6/README.md.
//
// Environment:
//   BASE_URL          Medusa base URL (default http://localhost:9000)
//   PUBLISHABLE_KEY   Store API key, sent as the x-publishable-api-key header

const BASE_URL = (__ENV.BASE_URL || "http://localhost:9000").replace(/\/+$/, "");
const PUBLISHABLE_KEY = __ENV.PUBLISHABLE_KEY || "";

export const options = {
  stages: [
    { duration: "30s", target: 10 }, // ramp up to 10 VUs
    { duration: "1m", target: 10 }, // hold at 10 VUs
    { duration: "30s", target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"], // < 1% failed requests
    http_req_duration: ["p(95)<800"], // 95% of requests under 800ms
    // Per-endpoint budgets: products is the heavier query.
    "http_req_duration{endpoint:store_regions}": ["p(95)<600"],
    "http_req_duration{endpoint:store_products}": ["p(95)<1000"],
  },
};

const storeParams = {
  headers: {
    "x-publishable-api-key": PUBLISHABLE_KEY,
    Accept: "application/json",
  },
};

export default function () {
  const regions = http.get(`${BASE_URL}/store/regions`, {
    ...storeParams,
    tags: { endpoint: "store_regions" },
  });
  check(regions, {
    "regions: status is 200": (r) => r.status === 200,
  });

  const products = http.get(`${BASE_URL}/store/products?limit=20`, {
    ...storeParams,
    tags: { endpoint: "store_products" },
  });
  check(products, {
    "products: status is 200": (r) => r.status === 200,
  });

  sleep(1);
}
