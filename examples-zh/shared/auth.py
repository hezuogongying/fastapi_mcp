# -*- coding: utf-8 -*-
"""
认证相关工具函数模块。

本模块包含用于处理认证逻辑的函数，例如从 JWKS (JSON Web Key Set) URL 获取公钥。
这些公钥通常用于验证 JWT (JSON Web Tokens) 的签名。
"""

from jwt.algorithms import RSAAlgorithm  # 从 PyJWT 库导入 RSA 算法，用于处理 JWK
from cryptography.hazmat.primitives import serialization  # 从 cryptography 库导入序列化模块，用于密钥格式转换
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey  # 从 cryptography 库导入 RSA 公钥类型

import logging  # 导入日志模块
import httpx  # 导入 httpx 库，用于异步 HTTP 请求

from examples_zh.shared.setup import setup_logging  # 从共享设置模块导入日志配置函数

setup_logging()  # 初始化日志配置

logger = logging.getLogger(__name__)  # 获取当前模块的 logger 实例


async def fetch_jwks_public_key(url: str) -> str:
    """
    从给定的 URL 获取 JWKS (JSON Web Key Set)，并提取主要的公钥（通常是第一个）为 PEM 格式。

    参数:
        url (str): 要从中获取 JWKS 的 URL。

    返回:
        str: PEM 格式的公钥字符串。

    异常:
        httpx.HTTPStatusError: 如果请求 JWKS URL 时发生 HTTP 错误。
        ValueError: 如果 JWKS 数据格式无效或无法提取 RSA 公钥。
    """
    logger.info(f"正在从以下地址获取 JWKS: {url}")  # 日志：开始获取 JWKS
    async with httpx.AsyncClient() as client:  # 创建异步 HTTP 客户端
        response = await client.get(url)  # 发送 GET 请求获取 JWKS 数据
        response.raise_for_status()  # 如果 HTTP 请求返回错误状态码，则抛出异常
        jwks_data = response.json()  # 解析响应的 JSON 数据

        # 校验 JWKS 数据格式是否正确
        if not jwks_data or "keys" not in jwks_data or not jwks_data["keys"]:
            logger.error("无效的 JWKS 数据格式：缺少 'keys' 数组或 'keys' 数组为空") # 日志：JWKS 格式错误
            raise ValueError("无效的 JWKS 数据格式：缺少 'keys' 数组或 'keys' 数组为空")

        # 通常 JWKS 可能包含多个密钥，这里简单地使用第一个密钥
        # 在实际应用中，可能需要根据 'kid' (Key ID) 等字段来选择正确的密钥
        jwk = jwks_data["keys"][0]  # 获取密钥列表中的第一个 JWK

        # 将 JWK 转换为 PEM 格式的公钥
        public_key = RSAAlgorithm.from_jwk(jwk)  # 使用 PyJWT 的 RSAAlgorithm 从 JWK 对象创建公钥对象
        
        # 确保转换后的公钥是 RSAPublicKey 类型
        if isinstance(public_key, RSAPublicKey):
            # 将 RSA 公钥对象序列化为 PEM 格式的字节串
            pem_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,  # 指定编码为 PEM
                format=serialization.PublicFormat.SubjectPublicKeyInfo,  # 指定公钥格式为 SubjectPublicKeyInfo
            )
            pem_str = pem_bytes.decode("utf-8")  # 将 PEM 格式的字节串解码为 UTF-8 字符串
            logger.info("成功从 JWKS 中提取公钥") # 日志：成功提取公钥
            return pem_str  # 返回 PEM 格式的公钥字符串
        else:
            # 如果从 JWK 解析出的不是预期的 RSA 公钥类型，则记录错误并抛出异常
            logger.error("无效的 JWKS 数据格式：期望得到 RSA 公钥") # 日志：非预期的密钥类型
            raise ValueError("无效的 JWKS 数据格式：期望得到 RSA 公钥")
