import http from "k6/http";
import { check, sleep } from "k6";

// Smoke test: minimal load against the read-only Store API endpoints the
// storefront depends on, plus /health. The goal is a quick "is it healthy and
// fast?" signal, not load. See k6/README.md for how to run it.
//
// Environment:
//   BASE_URL          Medusa base URL (default http://localhost:9000)
//   PUBLISHABLE_KEY   Store API key, sent as the x-publishable-api-key header

const BASE_URL = (__ENV.BASE_URL || "http://localhost:9000").replace(/\/+$/, "");
const PUBLISHABLE_KEY = __ENV.PUBLISHABLE_KEY || "";

export const options = {
  vus: 1,
  iterations: 5,
  thresholds: {
    // A smoke run must be clean: no failed requests and fast responses.
    http_req_failed: ["rate==0"],
    http_req_duration: ["p(95)<500"],
  },
};

function storeParams(endpoint) {
  return {
    headers: {
      "x-publishable-api-key": PUBLISHABLE_KEY,
      Accept: "application/json",
    },
    tags: { endpoint: endpoint },
  };
}

export default function () {
  // /health needs no publishable key and proves the runtime is up.
  const health = http.get(`${BASE_URL}/health`, { tags: { endpoint: "health" } });
  check(health, {
    "health: status is 200": (r) => r.status === 200,
  });

  const regions = http.get(`${BASE_URL}/store/regions`, storeParams("store_regions"));
  check(regions, {
    "regions: status is 200": (r) => r.status === 200,
    "regions: payload has regions[]": (r) =>
      r.status === 200 && Array.isArray(r.json("regions")),
  });

  const products = http.get(
    `${BASE_URL}/store/products?limit=10`,
    storeParams("store_products"),
  );
  check(products, {
    "products: status is 200": (r) => r.status === 200,
    "products: payload has products[]": (r) =>
      r.status === 200 && Array.isArray(r.json("products")),
  });

  sleep(1);
}
