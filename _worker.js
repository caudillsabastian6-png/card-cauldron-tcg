// ============================================================================
// ALTERNATIVE DEPLOY FILE — Cloudflare Pages "advanced mode" _worker.js
// ============================================================================
// This is the fallback for the eBay Marketplace Account Deletion endpoint,
// used INSTEAD OF functions/ebay-deletion-notifications.js when deploying
// through the Cloudflare DASHBOARD drag-and-drop uploader, which does NOT
// compile a functions/ folder (per Cloudflare's Direct Upload docs and
// Known Issues pages). A root-level _worker.js IS supported by dashboard
// direct upload.
//
// TO USE: place this file at the ROOT of the deploy package named exactly
//         "_worker.js" and remove the functions/ folder (when _worker.js is
//         present, Cloudflare ignores the /functions directory entirely).
//         A ready-made package with exactly that layout is provided as
//         card-cauldron-site-v2-worker.zip — prefer uploading that one.
//
// Behavior is identical to the Pages Function version:
//   GET  /ebay-deletion-notifications?challenge_code=<code>
//        -> 200 {"challengeResponse": sha256hex(challengeCode + token + endpointUrl)}
//   POST /ebay-deletion-notifications -> 200 acknowledgement
//   Everything else -> served from the static site assets.
// ============================================================================

const VERIFICATION_TOKEN = "-CJGs-AFy40JqT7Ev9lodZOAXHb3dNm8zlTS347s36_VL1--";
const ENDPOINT_URL = "https://cardcauldrontcg.com/ebay-deletion-notifications";
const ENDPOINT_PATH = "/ebay-deletion-notifications";

async function sha256Hex(text) {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function jsonResponse(body, status) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: { "content-type": "application/json" },
  });
}

async function handleGet(request) {
  const url = new URL(request.url);
  const challengeCode = url.searchParams.get("challenge_code");
  if (!challengeCode) {
    return jsonResponse({ error: "missing challenge_code query parameter" }, 400);
  }
  const challengeResponse = await sha256Hex(
    challengeCode + VERIFICATION_TOKEN + ENDPOINT_URL
  );
  return jsonResponse({ challengeResponse: challengeResponse }, 200);
}

async function handlePost(request) {
  try {
    await request.clone().json();
  } catch (e) {
    try {
      await request.text();
    } catch (e2) {
      /* body unreadable — acknowledge anyway */
    }
  }
  return jsonResponse({ status: "received" }, 200);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === ENDPOINT_PATH || url.pathname === ENDPOINT_PATH + "/") {
      if (request.method === "GET") return handleGet(request);
      if (request.method === "POST") return handlePost(request);
      return jsonResponse({ error: "method not allowed" }, 405);
    }
    // Everything else: the static site.
    return env.ASSETS.fetch(request);
  },
};
