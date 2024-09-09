from rpi_hardware_pwm import HardwarePWM
from time import sleep
import atexit
from src.logger.systemd_logger import SystemdLogger


class Servos:
    """Control the servo motors of the camera system"""
    def __init__(
        self,
        logger: SystemdLogger,
        pan_angle: float = 90.0,
        tilt_angle: float = 90.0,
        delta_angle: float = 10.0,
        min_angle: float = 0.0,
        max_angle: float = 180.0
    ) -> None:
        
        # register the cleanup function for when the instance is terminated
        atexit.register(self._cleanup)
        
        # initialise systemd logger
        self.logger = logger

        # initilise angle limits & delta angle
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._delta_angle = delta_angle

        # Initialize starting servo angles
        self._pan_angle = pan_angle
        self._tilt_angle = tilt_angle

        # Initialise servo PWM pins
        self._pan_servo = HardwarePWM(pwm_channel=1, hz=50, chip=2)
        self._tilt_servo = HardwarePWM(pwm_channel=0, hz=50, chip=2)
        self._pan_servo.start(self._angle_to_duty_cycle(self._pan_angle))
        self._tilt_servo.start(self._angle_to_duty_cycle(self._tilt_angle))

    def set_pan_angle(self, new_angle: int = 90) -> None:
        "Sets the pan angle."
        assert new_angle >= 0.0
        assert new_angle <= 180.0
        self._pan_angle = new_angle
        self.logger.log_info(f"new pan angle: {self._pan_angle}")
        self._pan_servo.change_duty_cycle(self._angle_to_duty_cycle(new_angle))

    def set_tilt_angle(self, new_angle: int = 90) -> None:
        "Sets the tilt angle."
        assert new_angle >= 0.0
        assert new_angle <= 180.0
        self._tilt_angle = new_angle
        self.logger.log_info(f"new tilt angle: {self._tilt_angle}")
        self._tilt_servo.change_duty_cycle(self._angle_to_duty_cycle(new_angle))

    def decr_pan(self) -> None:
        "Decrease the pan angle by the delta."
        if self._pan_angle >= self._delta_angle:
            self.set_pan_angle(self._pan_angle - self._delta_angle)

    def decr_tilt(self) -> None:
        "Decrease the tilt angle by the delta."
        if self._tilt_angle >= self._delta_angle:
            self.set_tilt_angle(self._tilt_angle - self._delta_angle)

    def incr_pan(self) -> None:
        "Increase the pan angle by the delta."
        if self._pan_angle <= self._max_angle - self._delta_angle:
            self.set_pan_angle(self._pan_angle + self._delta_angle)

    def incr_tilt(self) -> None:
        "Increase the tilt angle by the delta."
        if self._tilt_angle <= self._max_angle - self._delta_angle:
            self.set_tilt_angle(self._tilt_angle + self._delta_angle)

    def home(self) -> None:
        """Set the angles of both motors back to their home position"""
        self.set_pan_angle(90)
        self.set_tilt_angle(90)

    def _angle_to_duty_cycle(self, angle: float) -> float:
        """Convert the angle (degrees) to duty cycle of SG90 servo motor"""
        assert angle >= 0.0
        assert angle <= 180.0
        # SG90 servo parameters 2.5% to 12.5%
        dc = 2.5 + (angle / 18.0)
        self.logger.log_info(f"duty cycle: {dc}")
        return dc

    def _cleanup(self) -> None:
        """Cleanup the HardwarePWM classes"""
        self._pan_servo.stop()
        self._tilt_servo.stop()
