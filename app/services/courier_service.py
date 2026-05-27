import logging
import time
from typing import Dict, Any, Optional
from app.services.capi_service import get_http_client

logger = logging.getLogger(__name__)

PATHAO_BASE_URL = "https://api-hermes.pathao.com"
STEADFAST_BASE_URL = "https://portal.steadfast.com.bd"

# ─── Pathao Token Cache ────────────────────────────────────────────────────────
# Pathao OAuth2 tokens সাধারণত 1 ঘণ্টা valid থাকে। প্রতি request-এ নতুন token
# নেওয়ার বদলে 50 মিনিট cache করে রাখি — latency কমে + Pathao API rate limit এড়ায়।
_PATHAO_TOKEN_TTL = 50 * 60  # 50 minutes (safe margin before 1-hour expiry)
_pathao_token_cache: dict[str, tuple[str, float]] = {}  # cache_key -> (token, expires_at)


class CourierServiceException(Exception):
    pass

class CourierService:
    @staticmethod
    async def get_pathao_token(client_id: str, client_secret: str, store_owner_email: str, password: str) -> Optional[str]:
        """Pathao API Token সংগ্রহ করার জন্য OAuth2 Call। 50-minute TTL cache সহ।"""
        cache_key = f"{client_id}:{store_owner_email}"
        now = time.monotonic()

        # ─── Cache hit ────────────────────────────────────────────────────
        if cache_key in _pathao_token_cache:
            cached_token, expires_at = _pathao_token_cache[cache_key]
            if now < expires_at:
                return cached_token

        # ─── Cache miss — fetch new token ─────────────────────────────────
        url = f"{PATHAO_BASE_URL}/aladdin/api/v1/issue-token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": store_owner_email,
            "password": password,
            "grant_type": "password"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        client = await get_http_client()
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    _pathao_token_cache[cache_key] = (token, now + _PATHAO_TOKEN_TTL)
                return token
            else:
                logger.error(f"Pathao Token generation failed: {response.status_code} - {response.text}")
                # Auth failure — evict stale cache entry
                _pathao_token_cache.pop(cache_key, None)
                return None
        except Exception as e:
            logger.error(f"Exception during Pathao Token request: {e}")
            return None

    @classmethod
    async def send_to_pathao(
        cls,
        client_id: str,
        client_secret: str,
        email: str,
        password: str,
        store_id: str,
        recipient_name: str,
        recipient_phone: str,
        recipient_address: str,
        cod_amount: float,
        merchant_order_id: str,
        item_quantity: int = 1,
        item_weight: float = 0.5
    ) -> Dict[str, Any]:
        """Pathao Courier-এ অর্ডার প্লেস করা।"""
        token = await cls.get_pathao_token(client_id, client_secret, email, password)
        if not token:
            raise CourierServiceException("Failed to authenticate with Pathao API.")
            
        url = f"{PATHAO_BASE_URL}/aladdin/api/v1/orders"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "store_id": int(store_id),
            "merchant_order_id": merchant_order_id,
            "recipient_name": recipient_name,
            "recipient_phone": recipient_phone,
            "recipient_address": recipient_address,
            "recipient_city": 1, # Default Dhaka City (or dynamic based on address parsing later)
            "recipient_zone": 1, 
            "recipient_area": 1,
            "delivery_type": 48, # Default Normal Delivery (48 Hours)
            "item_type": 1,      # Default Document
            "item_quantity": item_quantity,
            "item_weight": item_weight,
            "amount_to_collect": cod_amount,
            "item_description": "Order from Buykori"
        }
        
        client = await get_http_client()
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                # Return formatted response
                order_data = data.get("data", {})
                return {
                    "success": True,
                    "courier_order_id": str(order_data.get("consignment_id")),
                    "tracking_id": str(order_data.get("consignment_id")),
                    "raw_response": data
                }
            else:
                logger.error(f"Pathao order placement failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": response.text
                }
        except Exception as e:
            logger.error(f"Exception during Pathao order: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    async def send_to_steadfast(
        cls,
        api_key: str,
        secret_key: str,
        recipient_name: str,
        recipient_phone: str,
        recipient_address: str,
        cod_amount: float,
        merchant_order_id: str
    ) -> Dict[str, Any]:
        """SteadFast Courier-এ অর্ডার প্লেস করা।"""
        url = f"{STEADFAST_BASE_URL}/api/v1/create_order"
        headers = {
            "Api-Key": api_key,
            "Secret-Key": secret_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "invoice": merchant_order_id,
            "recipient_name": recipient_name,
            "recipient_phone": recipient_phone,
            "recipient_address": recipient_address,
            "cod_amount": cod_amount,
            "note": "Order from Buykori"
        }
        
        client = await get_http_client()
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Check if Steadfast API internal success
                status = data.get("status")
                if status == 200:
                    order_data = data.get("order", {})
                    return {
                        "success": True,
                        "courier_order_id": str(order_data.get("id")),
                        "tracking_id": str(order_data.get("tracking_code")),
                        "raw_response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Unknown SteadFast API error")
                    }
            else:
                logger.error(f"SteadFast order placement failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": response.text
                }
        except Exception as e:
            logger.error(f"Exception during SteadFast order: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    async def check_steadfast_status(cls, api_key: str, secret_key: str, tracking_code: str) -> Optional[str]:
        """SteadFast-এর ট্র্যাক কোড দিয়ে স্ট্যাটাস চেক করা।"""
        url = f"{STEADFAST_BASE_URL}/api/v1/status_by_trackingcode/{tracking_code}"
        headers = {
            "Api-Key": api_key,
            "Secret-Key": secret_key,
            "Content-Type": "application/json"
        }
        
        client = await get_http_client()
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") # e.g. 'delivered', 'returned', 'in_transit'
            return None
        except Exception as e:
            logger.error(f"Failed to check SteadFast status: {e}")
            return None

    @classmethod
    async def check_pathao_status(
        cls,
        client_id: str,
        client_secret: str,
        email: str,
        password: str,
        consignment_id: str
    ) -> Optional[str]:
        """Pathao Consignment ID দিয়ে স্ট্যাটাস চেক করা।"""
        token = await cls.get_pathao_token(client_id, client_secret, email, password)
        if not token:
            return None
            
        url = f"{PATHAO_BASE_URL}/aladdin/api/v1/orders/{consignment_id}/info"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        client = await get_http_client()
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                order_data = data.get("data", {})
                return order_data.get("status") # e.g. 'delivered', 'returned'
            return None
        except Exception as e:
            logger.error(f"Failed to check Pathao status: {e}")
            return None

    @staticmethod
    def map_status(provider: str, raw_status: str) -> str:
        """বিভিন্ন কোরিয়ার সার্ভিসের স্ট্যাটাসকে আমাদের কমন সিস্টেমে ম্যাপ করা।"""
        raw_status = raw_status.lower().strip()
        
        if provider == "steadfast":
            # Steadfast statuses: 'delivered', 'returned', 'cancelled', 'in_transit', 'hold', 'pending'
            if raw_status in ("delivered", "completed"):
                return "delivered"
            elif raw_status in ("returned", "partial_returned"):
                return "returned"
            elif raw_status == "cancelled":
                return "cancelled"
            elif raw_status in ("in_transit", "picked_up", "shipped"):
                return "in_transit"
            else:
                return "pending"
                
        elif provider == "pathao":
            # Pathao statuses: 'pending', 'picked', 'in_transit', 'delivered', 'returned', 'cancelled'
            if raw_status == "delivered":
                return "delivered"
            elif raw_status == "returned":
                return "returned"
            elif raw_status == "cancelled":
                return "cancelled"
            elif raw_status in ("picked", "in_transit", "shipped"):
                return "in_transit"
            else:
                return "pending"
                
        return "pending"
