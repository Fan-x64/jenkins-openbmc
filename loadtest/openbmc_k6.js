import http from "k6/http";
import { check } from "k6";

export let options = { vus: 5, duration: "15s" };

export default function () {
  const res = http.get("https://127.0.0.1:2443/redfish/v1/", { timeout: '30s' });
  check(res, { "status 200": (r) => r.status === 200 });
}
