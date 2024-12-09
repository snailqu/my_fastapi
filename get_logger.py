import logging
import datetime


# 配置日志记录
def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    # 创建一个自定义的日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建一个文件处理器，写入日志到文件
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # 创建一个控制台处理器，输出日志到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 创建并配置日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 获取当前日期和时间，用于生成日志文件名称
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
log_file = f"./loggers/log_{current_time}.log"

# 初始化日志记录器
logger = setup_logger('my_logger', log_file, level=logging.DEBUG)

# 示例日志记录
if __name__ == "__main__":
    logger.debug("这是一个调试信息")
    logger.info("这是一个信息日志")
    logger.warning("这是一个警告日志")
    logger.error("这是一个错误日志")
    logger.critical("这是一个严重错误日志")

    try:
        # 故意制造一个异常
        1 / 0
    except ZeroDivisionError as e:
        logger.exception("捕获到一个异常：%s", e)