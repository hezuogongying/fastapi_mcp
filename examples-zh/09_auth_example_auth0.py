from fastapi import FastAPI, Depends, HTTPException, Request, status
from pydantic_settings import BaseSettings
from typing import Any
import logging

from fastapi_mcp import FastApiMCP, AuthConfig

from demo.core.auth import fetch_jwks_public_key
from demo.core.setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    要使本示例生效，需要在项目根目录下有一个 .env 文件，内容如下：
    AUTH0_DOMAIN=your-tenant.auth0.com
    AUTH0_AUDIENCE=https://your-tenant.auth0.com/api/v2/
    AUTH0_CLIENT_ID=your-client-id
    AUTH0_CLIENT_SECRET=your-client-secret
    """
    auth0_domain: str   # Auth0 域名，例如 "your-tenant.auth0.com"
    auth0_audience: str   # Audience，例如 "https://your-tenant.auth0.com/api/v2/"
    auth0_client_id: str
    auth0_client_secret: str

    @property
    def auth0_jwks_url(self):
        return f"https://{self.auth0_domain}/.well-known/jwks.json"

    @property
    def auth0_oauth_metadata_url(self):
        return f"https://{self.auth0_domain}/.well-known/openid-configuration"

    class Config:
        env_file = ".env"


settings = Settings()   # type: ignore


async def lifespan(app: FastAPI):
    app.state.jwks_public_key = await fetch_jwks_public_key(settings.auth0_jwks_url)
    logger.info(f"Auth0 client ID in settings: {settings.auth0_client_id}")
    logger.info(f"Auth0 domain in settings: {settings.auth0_domain}")
    logger.info(f"Auth0 audience in settings: {settings.auth0_audience}")
    yield


async def verify_auth(request: Request) -> dict[str, Any]:
    try:
        import jwt

        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证头部")

        token = auth_header.split(" ")[1]
        header = jwt.get_unverified_header(token)

        # 检查是否为 JWE 加密 token
        if header.get("alg") == "dir" and header.get("enc") == "A256GCM":
            raise ValueError(
                "Token 是加密的，无法离线验证。通常是因为请求 token 时未指定 audience。"
            )

         # 否则为 JWT，可离线验证
        if header.get("alg") in ["RS256", "HS256"]:
            claims = jwt.decode(
                token,
                app.state.jwks_public_key,
                algorithms=["RS256", "HS256"],
                audience=settings.auth0_audience,
                issuer=f"https://{settings.auth0_domain}/",
                options={"verify_signature": True},
            )
            return claims

    except Exception as e:
        logger.error(f"认证错误: {str(e)}")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")


async def get_current_user_id(claims: dict = Depends(verify_auth)) -> str:
    user_id = claims.get("sub")
    if not user_id:
        logger.error("Token 中未找到用户 ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")
    return user_id

app = FastAPI(lifespan=lifespan)


@app.get("/public")
def public():
    return {"message": "公共接口，无需认证"}


@app.get("/protected")
def protected(user_id: str = Depends(get_current_user_id)):
    return {"message": f"受保护接口，用户 ID: {user_id}"}


# 配置 FastAPI-MCP，集成 Auth0 认证
auth0_mcp = FastApiMCP(
    app,
    name="Auth0 认证的 MCP",
    auth_config=AuthConfig(
        dependencies=[Depends(get_current_user_id)],
    ),
)
auth0_mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
