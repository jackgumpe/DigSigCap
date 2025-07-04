from loguru import logger
import sys
import os
import platform

def setup_logger(name, level="DEBUG", rotation="100 MB"):
    """Configure Loguru logger with Windows-specific settings"""
    
    # Remove default handler
    logger.remove()
    
    # Windows-specific log path
    if platform.system() == "Windows":
        log_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'DigitalSignalCapture', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"app_{name}.log")
    else:
        log_file = f"logs/app_{name}.log"
    
    # Add stdout handler
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler
    logger.add(
        log_file,
        rotation=rotation,
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True
    )
    
    return logger