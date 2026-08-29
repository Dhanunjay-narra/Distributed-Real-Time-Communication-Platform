import uuid, time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from packages.common.logger import set_correlation_id, set_user_id, get_logger
from packages.security.jwt import decode_token
from packages.security.rate_limiter import DistributedRateLimiter

logger = get_logger("api-gateway")
rate_limiter = DistributedRateLimiter()

class GatewayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(corr_id)

        client_ip = request.client.host if request.client else "127.0.0.1"
        try:
            await rate_limiter.check_rate_limit(f"ip:{client_ip}", limit=120, window_seconds=60)
        except Exception:
            return JSONResponse(status_code=429, content={"error": "Rate limit exceeded. Please slow down."})

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                claims = decode_token(token)
                set_user_id(claims.sub)
            except Exception:
                pass

        start_time = time.time()
        response: Response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Correlation-ID"] = corr_id
        response.headers["X-Response-Time-Ms"] = str(process_time_ms)
        return response
