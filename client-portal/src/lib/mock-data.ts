/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { CAPIEvent, APILog, Suggestion, UserProfile, ClientConnection, EventRule, Platform } from '../types';

export const initialProfile: UserProfile = {
  name: "Malcolm Abbott",
  email: "malcolmabbotte@gmail.com",
  notificationEmail: "malcolmabbotte@gmail.com",
  plan: "Growth Plan",
  eventsUsed: 12450,
  eventsQuota: 50000,
  renewalDate: "2026-06-24",
};

export const initialConnection: ClientConnection = {
  token: "",
  wpVersion: "6.4.3",
  lastHeartbeat: "2026-05-24T13:10:12Z",
  status: "Active",
};

export const initialRules: EventRule[] = [
  { eventName: "PageView", metaEnabled: true, tiktokEnabled: true, ga4Enabled: true },
  { eventName: "AddToCart", metaEnabled: true, tiktokEnabled: true, ga4Enabled: true },
  { eventName: "InitiateCheckout", metaEnabled: true, tiktokEnabled: true, ga4Enabled: true },
  { eventName: "Purchase", metaEnabled: true, tiktokEnabled: true, ga4Enabled: true },
  { eventName: "Lead", metaEnabled: true, tiktokEnabled: false, ga4Enabled: true },
  { eventName: "Contact", metaEnabled: false, tiktokEnabled: false, ga4Enabled: true },
];

export const staticFAQs = [
  {
    q: "How does Conversions API bypass client-side ad blockers?",
    a: "Unlike browser trackers that are blocked by browser lists (like EasyList), server-side events are routed from your self-hosted WordPress server directly to our cloud servers, which connect to Meta, TikTok, and Google via secure HTTP API requests on a back-channel. This bypasses ad-block extensions, Brave Shields, and content filters entirely."
  },
  {
    q: "Why are my events showing as 'Retrying' or 'Failed'?",
    a: "This normally indicates a credential issue or that the target platform's API endpoint returned a non-200 response (e.g., expired access token or invalid pixel size configuration). Click on the event in the Logs page to see the exact HTTP response code and payload details, then verify your Platform Credentials."
  },
  {
    q: "How does Deduplication work with browser-side pixel tracking?",
    a: "To prevent double-counting when utilizing both a browser pixel and server-side tracking, we transmit a matching `Event ID` and `Name` on both channels. Meta/TikTok matches these identifiers. If both are received within 48 hours, the browser event is usually preferred and the server event is deduplicated, ensuring safe reporting."
  },
  {
    q: "What does Event Match Quality mean in Meta CAPI?",
    a: "Match quality represents how many customer identifiers (like email hashes, phone numbers, state, country, IP address, user agents) were attached to your event. Passing more data points helps Meta locate the exact customer profile, raising your optimization from ~40% to ~90% for purchase tracking."
  }
];

export const initialSuggestions: Suggestion[] = [
  {
    id: "s_01",
    title: "Missing 'value' and 'currency' parameters on Purchase",
    severity: "Critical",
    explanation: "Your Purchase event is missing core transaction variables (`value`, `currency`). Meta Conversions API relies on value data for catalog pairings, value-based lookalike audiences, and ROAS calculations. This reduces your match quality and optimizer leverage by ~40%.",
    fixAction: "Navigate to WordPress > CAPI Plugin Settings > Event Parameters and check the box to 'Inherit WooCommerce Price & Currency Schema' automatically.",
    resolved: false,
    platform: "Meta CAPI"
  },
  {
    id: "s_02",
    title: "GA4 Events experiencing elevated failure rate (12%)",
    severity: "Warning",
    explanation: "Events sent to the Google Analytics 4 Measurement Protocol have been rejected with a 4xx response code during the last 7 days. This typically happens when the Measurement ID is mismatched or the 'API Secret Key' created in your GA4 admin workspace is expired or invalid.",
    fixAction: "Go to Admin > Data Streams > Web Stream > Measurement Protocol API Secrets in your GA4 account, generate a new secret token, and copy it into the Setup panel.",
    resolved: false,
    platform: "GA4"
  },
  {
    id: "s_03",
    title: "Duplicate AddToCart events transmitted without Deduplication keys",
    severity: "Critical",
    explanation: "We detected AddToCart payloads matching browser signals that are missing the mandatory deduplication `event_id`. This causes Meta Ads Manager to record double action triggers, skewing attribution numbers and inflating reported cart conversions artificially.",
    fixAction: "In your WooCommerce pixel setup tool, verify that 'Deduplication Sync Header' is toggled ON to match both pixel keys and track hashes.",
    resolved: false,
    platform: "Meta CAPI"
  },
  {
    id: "s_04",
    title: "TikTok tracking connection needs Optimization Review",
    severity: "Tip",
    explanation: "TikTok Events API is actively recording events, but is not receiving user agents or IP addresses. It is recommended to pass hashed identifiers (`em`, `ph`) or client headers to improve Match Quality on mobile-first campaigns.",
    fixAction: "Toggle on 'Advanced Customer Header Matching' in your WordPress settings panel.",
    resolved: false,
    platform: "TikTok Events API"
  }
];

// Seed realistic tracking history (last 30 days) to populate dashboards
export function generateEventData(): CAPIEvent[] {
  const events: CAPIEvent[] = [];
  const names = ['PageView', 'AddToCart', 'InitiateCheckout', 'Purchase', 'Lead', 'Contact'];
  const platforms: Platform[] = ['Meta CAPI', 'TikTok Events API', 'GA4'];
  const now = new Date();

  // Create ~120 realistic events over the past 30 days
  for (let i = 0; i < 150; i++) {
    const ageInHours = i * 4.8; // stagger events
    const date = new Date(now.getTime() - ageInHours * 60 * 60 * 1000);
    const platform = platforms[i % platforms.length];
    const name = names[Math.floor((i * 1.7) % names.length)];
    const id = `evt_${100000 + i}`;
    const dedupeKey = `did_${800000 + i}`;
    
    // Status bias: mostly success, occasional failure or retry
    let status: 'Success' | 'Failed' | 'Retry' = 'Success';
    let httpCode = 200;
    if (i % 23 === 0) {
      status = 'Failed';
      httpCode = 400;
    } else if (i % 37 === 0) {
      status = 'Retry';
      httpCode = 503;
    }

    const value = (120 - (i % 12) * 8).toFixed(2);
    const currency = 'USD';
    const emailHash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'; // SHA256 hashed

    const payload = {
      event_name: name,
      event_time: Math.floor(date.getTime() / 1000),
      event_id: dedupeKey,
      user_data: {
        client_ip_address: `192.168.1.${10 + (i % 50)}`,
        client_user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        em: name === 'Purchase' || name === 'Lead' ? [emailHash] : undefined,
      },
      custom_data: name === 'Purchase' ? {
        value: value,
        currency: currency,
        content_type: "product",
        contents: [
          { id: `prod_${i % 10}`, quantity: 1, item_price: parseFloat(value) }
        ]
      } : undefined,
    };

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${platform === 'Meta CAPI' ? 'fb_cap_key_***' : platform === 'TikTok Events API' ? 'tt_evt_key_***' : 'ga_mp_sec_***'}`,
      'X-Client-IP': `192.168.1.${10 + (i % 50)}`,
      'User-Agent': 'WordPress/6.4.3; WooCommerce/8.5.2',
    };

    const responseBody = status === 'Success' 
      ? { events_received: 1, status: "accepted", fb_trace_id: `FBT_${Math.random().toString(36).substring(7).toUpperCase()}` }
      : status === 'Retry'
        ? { error: { message: "Server overloaded", code: 503 } }
        : { error: { message: "Invalid conversion details: value missing on purchase event", code: 400, type: "OAuthException" } };

    events.push({
      id,
      timestamp: date.toISOString(),
      name,
      platform,
      status,
      httpCode,
      deduplicationKey: dedupeKey,
      payload,
      headers,
      responseBody,
      latencyMs: 75 + (i % 200),
    });
  }

  return events;
}

export function generateAPILogs(events: CAPIEvent[]): APILog[] {
  return events.map(evt => {
    const urls = {
      'Meta CAPI': 'https://graph.facebook.com/v18.0/pixel_id/events',
      'TikTok Events API': 'https://open-api.tiktok.com/v1.3/pixel/track',
      'GA4': 'https://www.google-analytics.com/mp/collect?api_secret=sec_key&measurement_id=id'
    };

    return {
      id: `api_${evt.id.split('_')[1]}`,
      timestamp: evt.timestamp,
      platform: evt.platform,
      endpoint: urls[evt.platform],
      method: 'POST',
      statusCode: evt.httpCode,
      latencyMs: evt.latencyMs,
      retryCount: evt.status === 'Retry' ? 1 : evt.status === 'Failed' ? 2 : 0,
      requestBody: JSON.stringify(evt.payload, null, 2),
      responseBody: JSON.stringify(evt.responseBody, null, 2)
    };
  });
}
