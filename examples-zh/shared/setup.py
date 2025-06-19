# -*- coding: utf-8 -*-
"""
共享设置模块，主要用于配置应用程序的日志记录。

本模块定义了一个基于 Pydantic 的日志配置模型 (LoggingConfig)
以及一个用于应用这些配置的函数 (setup_logging)。
这样可以方便地在应用的不同部分统一和管理日志行为。
"""

import logging  # 导入 Python 内置的日志模块

from pydantic import BaseModel  # 导入 Pydantic 的 BaseModel，用于创建数据模型


class LoggingConfig(BaseModel):
    """
    日志配置模型。

    使用 Pydantic BaseModel 定义日志系统的各项配置参数。
    这些参数将被 `logging.config.dictConfig` 用于配置日志记录器。
    """
    LOGGER_NAME: str = "fastapi_mcp"  # 默认的日志记录器名称
    LOG_FORMAT: str = "%(levelprefix)s %(asctime)s\t[%(name)s] %(message)s"  # 日志输出格式
    LOG_LEVEL: str = logging.getLevelName(logging.DEBUG)  # 默认日志级别 (DEBUG)

    version: int = 1  # 日志配置的版本，固定为 1
    disable_existing_loggers: bool = False  # 是否禁用已存在的日志记录器，通常设置为 False
    
    # 定义日志格式化器
    formatters: dict = {
        "default": {  # 默认格式化器
            "()": "uvicorn.logging.DefaultFormatter",  # 使用 uvicorn 的默认格式化器类
            "fmt": LOG_FORMAT,  # 应用上面定义的日志格式
            "datefmt": "%Y-%m-%d %H:%M:%S",  # 日期时间格式
        },
    }
    
    # 定义日志处理器
    handlers: dict = {
        "default": {  # 默认处理器
            "formatter": "default",  # 使用上面定义的 'default' 格式化器
            "class": "logging.StreamHandler",  # 使用 StreamHandler 将日志输出到流
            "stream": "ext://sys.stdout",  # 指定输出流为标准输出 (sys.stdout)
        },
    }
    
    # 定义日志记录器
    loggers: dict = {
        "": {  # 根日志记录器配置
            "handlers": ["default"],  # 使用 'default' 处理器
            "level": LOG_LEVEL,  # 设置为上面定义的日志级别
        },
        "uvicorn": {  # uvicorn 服务器的日志记录器配置
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
        LOGGER_NAME: {  # 自定义应用日志记录器 (fastapi_mcp) 的配置
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
    }


def setup_logging():
    """
    配置并初始化应用程序的日志系统。

    该函数会实例化 LoggingConfig 模型，并将其转换为字典格式，
    然后传递给 `logging.config.dictConfig` 来应用日志配置。
    """
    from logging.config import dictConfig  # 导入 Python 日志配置工具

    logging_config_instance = LoggingConfig()  # 创建 LoggingConfig 模型的实例
    # 将 Pydantic 模型实例转换为字典，然后应用到日志配置中
    dictConfig(logging_config_instance.model_dump())
