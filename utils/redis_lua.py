"""
Lua Scripts (Atomic) cho Event Registration.

Mã trả về:
  2  → Idempotent HIT – request này đã được xử lý thành công trước đó, trả Success ngay
  1  → Thành công lần đầu – tiến hành lưu DB
  0  → Đang có request khác cùng idempotency-key đang xử lý (PROCESSING)
 -1  → User đã đăng ký sự kiện này rồi (duplicate trong Redis Set)
 -2  → Sự kiện đã hết chỗ (Sold out)
 -3  → Cooldown – request trước vừa thất bại, chờ TTL ngắn rồi thử lại
"""

LUA_REGISTER_SCRIPT = """
local users_set_key    = KEYS[1]
local idempotency_key  = KEYS[2]

local user_id          = ARGV[1]
local max_participants = tonumber(ARGV[2])
local ttl_seconds      = tonumber(ARGV[3])

-- 1. Idempotency check
local status = redis.call("GET", idempotency_key)
if status == "COMPLETED" then return 2 end
if status == "PROCESSING" then return 0 end
if status == "FAILED" then return -3 end

-- 2. Lock request (PROCESSING)
redis.call("SET", idempotency_key, "PROCESSING", "EX", ttl_seconds)

-- 3. Check duplicate registration
if redis.call("SISMEMBER", users_set_key, user_id) == 1 then
    return -1
end

-- 4. Check & Reserve slot (luôn kiểm tra max_participants)
local count = redis.call("SCARD", users_set_key)
if count >= max_participants then
    redis.call("SET", idempotency_key, "FAILED", "EX", 10)
    return -2
end

-- 5. Commit state
redis.call("SADD", users_set_key, user_id)
redis.call("SET", idempotency_key, "COMPLETED", "EX", ttl_seconds)

return 1
"""

LUA_ROLLBACK_SCRIPT = """
local users_set_key    = KEYS[1]
local idempotency_key  = KEYS[2]

local user_id          = ARGV[1]

-- 1. Chỉ hoàn trả slot bằng cách xóa user khỏi Set
redis.call("SREM", users_set_key, user_id)

-- 2. Đánh dấu FAILED để cho phép retry sau 5s
redis.call("SET", idempotency_key, "FAILED", "EX", 5)

return 1
"""

import uuid
from configs.redis_config import get_redis

# ========================
# CONFIG & KEYS
# ========================
_IDEMPOTENCY_TTL = 86400
_SLOT_KEY_TTL = 172800

def _users_key(event_id: str) -> str:
    return f"event:{event_id}:users"

def _init_key(event_id: str) -> str:
    return f"event:{event_id}:init"

def _idempotency_key(raw_key: str | None, event_id: str, user_id: str) -> str:
    # Nếu client không gửi key, dùng auto-key dựa trên user+event để chặn double-click
    return raw_key or f"auto:{event_id}:{user_id}"

# ========================
# LUA EXECUTION
# ========================
async def run_lua(event_id: str, user_id: str, max_p: int, raw_key: str | None) -> int:
    redis = get_redis()
    u_key = _users_key(event_id)
    i_key = _idempotency_key(raw_key, event_id, user_id)
    init_key = _init_key(event_id)
    
    # 1. Lazy sync from DB if Redis Set is missing or expired
    if not await redis.exists(init_key):
        lock_key = f"lock:init:{event_id}"
        # Lock 30s để tránh nhiều instance cùng nạp DB đồng thời
        if await redis.set(lock_key, "1", nx=True, ex=30):
            try:
                # Nạp danh sách User ID hiện tại từ DB vào Redis Set
                from beanie import PydanticObjectId
                from repositories.event_registration_repo import EventRegistrationRepository
                
                user_ids = await EventRegistrationRepository.list_user_ids_by_event(PydanticObjectId(event_id))
                if user_ids:
                    await redis.sadd(u_key, *[str(uid) for uid in user_ids])
                
                # Set TTL cho Set và Key đánh dấu đã khởi tạo
                await redis.expire(u_key, _SLOT_KEY_TTL)
                await redis.set(init_key, "1", ex=_SLOT_KEY_TTL)
            finally:
                await redis.delete(lock_key)

    # 2. Thực thi Lua Script
    return int(await redis.eval(
        LUA_REGISTER_SCRIPT,
        2,
        u_key,
        i_key,
        user_id,
        str(max_p),
        str(_IDEMPOTENCY_TTL),
    ))

async def rollback(event_id: str, user_id: str, max_p: int, raw_key: str | None) -> None:
    try:
        redis = get_redis()
        await redis.eval(
            LUA_ROLLBACK_SCRIPT,
            2,
            _users_key(event_id),
            _idempotency_key(raw_key, event_id, user_id),
            user_id,
        )
    except Exception:
        pass  # Best-effort

