"""Common simple utilities that could make life easier for everyone."""

import datetime
import time


class Rate:  # pylint: disable=too-few-public-methods
    """Rate object to sleep in a loop to maintain a constant rate."""

    def __init__(self, period_sec: float, warn_threshold: float = 0.1):
        """Initialize the rate object.

        :param period_sec: The period in seconds.
        :param warn_threshold: The threshold to print a warning if the rate is
            slower than the period.
        """
        self._period_sec = period_sec
        self._warn_threshold_sec = -1 * warn_threshold * period_sec
        self._last_time = time.monotonic()

    def sleep(self):
        """Sleep to maintain the rate."""
        sleep_time = self._last_time + self._period_sec - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)
        elif sleep_time < self._warn_threshold_sec:
            print("WARNING: Rate is too slow!")
        self._last_time = time.monotonic()


def get_datetime_str(
    time_start: datetime.datetime = datetime.datetime.now(),
) -> str:
    """Return a string of the current date and time.

    :param time_start: The start time.(Optional)
    :return: The string of the current date and time.
    """
    return time_start.strftime("%Y%m%d%H%M%S")
