# %%
import logging

# %%
# ----------------------------------------------------------------
# Main setup for signal protocol
main_setup = dict(
    sample_rate=1000,  # Hz
    interval=40,  # milliseconds
    channels=64,  # channels
    header_length=22,  # header length
)

# ----------------------------------------------------------------
# Signal sender setup
signal_sender_setup = dict(
    host='localhost',
    port=23333
)

# ----------------------------------------------------------------
# Data center setup
data_center_setup = dict(
    host='localhost',
    port=23334
)

# %%
default_logging_kwargs = dict(
    name='EPD',
    filepath='log/epd.log',
    level_file=logging.DEBUG,
    level_console=logging.DEBUG,
    format_file='%(asctime)s %(name)s %(levelname)-8s %(message)-40s {{%(filename)s:%(lineno)s:%(module)s:%(funcName)s}}',
    format_console='%(asctime)s %(name)s %(levelname)-8s %(message)-40s {{%(filename)s:%(lineno)s}}'
)


def generate_logger(name, filepath, level_file, level_console, format_file, format_console):
    '''
    Generate logger from inputs,
    the logger prints message both on the console and into the logging file.
    The DEFAULT_LOGGING_KWARGS is provided to automatically startup

    Args:
        :param:name: The name of the logger
        :param:filepath: The logging filepath
        :param:level_file: The level of logging into the file
        :param:level_console: The level of logging on the console
        :param:format_file: The format when logging on the console
        :param:format_console: The format when logging into the file
    '''

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(filepath)
    file_handler.setFormatter(logging.Formatter(format_file))
    file_handler.setLevel(level_file)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_console))
    console_handler.setLevel(level_console)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = generate_logger(**default_logging_kwargs)

# %%
