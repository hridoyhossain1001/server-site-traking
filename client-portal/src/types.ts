/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type Platform = 'Meta CAPI' | 'TikTok Events API' | 'GA4';

export type EventStatus = 'Success' | 'Failed' | 'Retry';

export interface CAPIEvent {
  id: string;
  timestamp: string;
  name: string;
  platform: Platform;
  status: EventStatus;
  httpCode: number;
  deduplicationKey: string;
  payload: any;
  headers: Record<string, string>;
  responseBody: any;
  latencyMs: number;
}

export interface APILog {
  id: string;
  timestamp: string;
  platform: Platform;
  endpoint: string;
  method: 'POST' | 'GET' | 'PUT';
  statusCode: number;
  latencyMs: number;
  retryCount: number;
  requestBody: string;
  responseBody: string;
}

export interface OutboxItem {
  id: number;
  status: 'queued' | 'processing' | 'dead' | 'sent';
  attempts: number;
  maxAttempts: number;
  nextAttemptAt: string | null;
  lastError: string;
  createdAt: string;
  sentAt: string | null;
  locked: boolean;
  eventNames: string[];
  eventCount: number;
  eventIds: string[];
}

export interface PlatformConfig {
  enabled: boolean;
  pixelIdOrMeasurementId: string;
  accessToken: string;
  testEventCode?: string;
  status: 'Valid' | 'Invalid' | 'Untested';
}

export interface EventRule {
  eventName: string;
  metaEnabled: boolean;
  tiktokEnabled: boolean;
  ga4Enabled: boolean;
}

export interface ClientConnection {
  token: string;
  wpVersion: string;
  lastHeartbeat: string;
  status: 'Active' | 'Degraded' | 'Disconnected';
  api_key?: string;
}

export interface UserProfile {
  name: string;
  email: string;
  notificationEmail: string;
  plan: string;
  eventsUsed: number;
  eventsQuota: number;
  renewalDate: string;
}

export interface Suggestion {
  id: string;
  title: string;
  severity: 'Critical' | 'Warning' | 'Tip';
  explanation: string;
  fixAction: string;
  resolved: boolean;
  platform?: Platform;
}

export interface CampaignPayload {
  platform: Platform;
  eventName: string;
  value?: string;
  currency?: string;
  email?: string;
  phone?: string;
  ip?: string;
  userAgent?: string;
  customParams?: Record<string, any>;
}

export interface CourierSettings {
  pathao_api_key?: string;
  pathao_secret_key?: string;
  pathao_store_id?: string;
  steadfast_api_key?: string;
  steadfast_secret_key?: string;
  courier_auto_send: boolean;
  default_courier?: string;
}

export interface CourierOrder {
  id: number;
  order_id: string;
  courier_provider: string;
  courier_order_id?: string;
  courier_tracking_id?: string;
  courier_status: string;
  recipient_name?: string;
  recipient_phone?: string;
  recipient_address?: string;
  cod_amount: number;
  delivery_charge: number;
  created_at: string;
  purchase_event_sent: boolean;
}

