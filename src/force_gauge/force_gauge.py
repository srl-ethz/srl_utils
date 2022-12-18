"""Utility class for reading force gauge data.

Works with the RS-Pro 111-3689 1-axis Force Gauge.
The force gauge is connected to the computer via a 3.5mm single channel
audio jack that is wired to a DB9 connector (see specification in
docs/force_gauge-datasheet.pdf) through an RS-232 to USB converter.
"""

import signal
import sys
import threading
import time

import serial


class ForceGauge:  # pylint: disable=too-many-instance-attributes
    # Justification: these attributes are needed to handle the force sensor state machine.
    """Utility class for reading force gauge data."""

    START_WORD = b"\x02"
    END_WORD = b"\r"
    CONSTANT_g = 9.810

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        """Initialize serial port to connect to force gauge."""
        self.serial = serial.Serial(port=port, baudrate=baudrate)

        self._byte_index = 0

        self.gauge_lock = threading.Lock()
        self.force_val = 0
        self.force_unit = None
        self.force_sign = 0
        self.force_decimal = 0
        self.force_raw = 0
        self.force_updated_time = 0

        self.exit_trigerred = threading.Event()
        self.update_state_thread = threading.Thread(
            target=self._update_state_loop
        )
        # self.update_state_freq = 50
        self.update_state_thread.start()

    def _read_next_byte(self):
        """Read and return data from gauge and handle errors."""
        new_byte = self.serial.read()
        return new_byte

    def _update_state_loop(self):
        """Read force gauge data and update state machine based on received data.

        Called by a thread to continuously update the state machine.
        """
        while not self.exit_trigerred.is_set():
            try:
                self._update_gauge_state_machine()
            except ValueError as error:
                print(error)

    def _update_gauge_state_machine(
        self,
    ):  # pylint: disable=too-many-branches, disable=too-many-statements
        #  Justification: the branches are necessary to handle the state machine.
        #  Justification: doesn't make sense to break this up into smaller functions.
        """Update state machine based on received data from force gauge."""
        new_byte = self._read_next_byte()

        # D15: Start Word
        if self._byte_index == 0:
            if new_byte == ForceGauge.START_WORD:
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected start word but received {str(new_byte)} instead"
                )
                self._byte_index = 0

        # D14: expect '4'
        elif self._byte_index == 1:
            if new_byte == b"4":
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected '4' but received {str(new_byte)} instead"
                )
                self._byte_index = 0

        # D13: expect '1'
        elif self._byte_index == 2:
            if new_byte == b"1":
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected '1' but received {str(new_byte)} instead"
                )
                self._byte_index = 0

        # D12: expect '5'
        elif self._byte_index == 3:
            if new_byte == b"5":
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected '5' but received {str(new_byte)} instead"
                )
                self._byte_index = 0

        # D11: set unit of force
        elif self._byte_index == 4:
            # set to kg
            if new_byte == b"5":
                self.force_unit = "kg"
                self._byte_index += 1
            # set to LB
            elif new_byte == b"6":
                self.force_unit = "LB"
                self._byte_index += 1
            # set to g
            elif new_byte == b"7":
                self.force_unit = "g"
                self._byte_index += 1
            # set to oz
            elif new_byte == b"8":
                self.force_unit = "oz"
                self._byte_index += 1
            # set to Newton
            elif new_byte == b"9":
                self.force_unit = "Newton"
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected number btw 5-9 but received {str(new_byte)} instead"
                )
                self._byte_index = 0

        # D10: set sign
        elif self._byte_index == 5:
            # Force has positive sign
            if new_byte == b"0":
                self.force_sign = 1
                self._byte_index += 1
            # Force has negative sign
            elif new_byte == b"1":
                self.force_sign = -1
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected '0' or '1' but received {str(new_byte)} instead"
                )
                self._byte_index = 0
        # D9: set decimal point (dp)
        elif self._byte_index == 6:
            # No dp
            floatingpoint_position = int(new_byte)
            if 0 <= floatingpoint_position < 4:
                self.force_decimal = 10 ** (-floatingpoint_position)
                self._byte_index += 1
            else:
                print(
                    f"ERROR: Expected number btw 0-3 but received {str(new_byte)} instead"
                )
                self._byte_index = 0
            # D8 to D1 set raw force
        elif self._byte_index >= 7 and self._byte_index < 15:
            self.force_raw = self.force_raw * 10
            self.force_raw += float(new_byte)
            self._byte_index += 1
        # D15: End Word
        elif self._byte_index == 15:
            if new_byte == ForceGauge.END_WORD:
                self._byte_index = 0
                with self.gauge_lock:
                    self.force_val = (
                        self.force_raw * self.force_decimal * self.force_sign
                    )
                    self.force_updated_time = time.time()
                    self.force_raw = 0.0
                    self.force_decimal = 0
                    self.force_sign = 1
                # print(f"done reading bytes Force is: {self.force_val}")
            else:
                print(
                    f"ERROR: Expected start word but received {str(new_byte)} instead"
                )
                self._byte_index = 0

    def read_gauge(self):
        """Thread-safe function to read force gauge data.

        Returns: force value, unit (as set on the force gauge), time since last update.
        """
        with self.gauge_lock:
            return (
                self.force_val,
                self.force_unit,
                time.time() - self.force_updated_time,
            )

    def read_force(self):
        """Thread-safe function to read force in Newtons."""
        sensor_reading, unit, update_time = self.read_gauge()
        conversion_factor = 1  # default to Newtons
        if unit == "g":
            # convert grams to Newtons
            conversion_factor = ForceGauge.CONSTANT_g * 1e-3
        elif unit == "kg":
            # convert kg to Newtons
            conversion_factor = sensor_reading * ForceGauge.CONSTANT_g
        return sensor_reading * conversion_factor, update_time

    def signal_handler(self, sig, frame):  # pylint: disable=unused-argument
        #  Justification: arguments are required by signal.signal
        """Handle SIGINT signal."""
        self.exit_trigerred.set()
        self.update_state_thread.join()
        sys.exit(0)


if __name__ == "__main__":
    fg = ForceGauge()
    signal.signal(signal.SIGINT, fg.signal_handler)

    while not fg.exit_trigerred.is_set():
        try:
            print(f"Force gauge reading: {fg.read_gauge()}")
            time.sleep(0.1)
        except NotImplementedError:
            print("Caught NotImplementedError")
            fg.exit_trigerred.set()
    fg.update_state_thread.join()
