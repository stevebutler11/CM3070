import pytest
from unittest.mock import MagicMock, patch
from src.servos.servos import Servos
from src.logger.systemd_logger import SystemdLogger


@pytest.fixture
def mock_hardware_pwms():
    with patch("src.servos.servos.HardwarePWM") as MockPWM:
        # Create individual mock instances for pan and tilt servos
        mock_pan_servo = MagicMock()
        mock_tilt_servo = MagicMock()

        # when the mocked HardwarePWM is called twice in __init__ in Servos,
        # the first time it gets mock_pan_servo, the second mock_tilt_servo.
        # this way we can test the values of each appropriately
        MockPWM.side_effect = [mock_pan_servo, mock_tilt_servo]

        yield mock_pan_servo, mock_tilt_servo


@pytest.fixture
def mock_logger():
    mock_logger = MagicMock(SystemdLogger)
    yield mock_logger


def test_initialization(mock_hardware_pwms, mock_logger):
    """test the default initialisation of the Servos class works as expected"""
    mock_pan_servo, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger)

    # assert init values correct
    assert servos._min_angle == 0.0
    assert servos._max_angle == 180.0
    assert servos._delta_angle == 10.0
    assert servos._pan_angle == 90.0
    assert servos._tilt_angle == 90.0

    mock_pan_servo.start.assert_any_call(servos._angle_to_duty_cycle(90.0))
    mock_tilt_servo.start.assert_any_call(servos._angle_to_duty_cycle(90.0))


def test_non_default_initialization(mock_hardware_pwms, mock_logger):
    """test the non-default initialisation of the Servos class works as expected"""
    mock_pan_servo, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(
        logger=mock_logger, pan_angle=100.0, tilt_angle=80.0, delta_angle=5.0
    )

    # assert init values correct
    assert servos._min_angle == 0.0
    assert servos._max_angle == 180.0
    assert servos._delta_angle == 5.0
    assert servos._pan_angle == 100.0
    assert servos._tilt_angle == 80.0

    mock_pan_servo.start.assert_any_call(servos._angle_to_duty_cycle(100.0))
    mock_tilt_servo.start.assert_any_call(servos._angle_to_duty_cycle(80.0))


def test_set_pan_angle(mock_hardware_pwms, mock_logger):
    """test setting the pan servo angle"""
    mock_pan_servo, _ = mock_hardware_pwms

    servos = Servos(logger=mock_logger)
    servos.set_pan_angle(120)

    assert servos._pan_angle == 120

    mock_pan_servo.change_duty_cycle.assert_called_with(
        servos._angle_to_duty_cycle(120)
    )


def test_incr_pan(mock_hardware_pwms, mock_logger):
    """test incrementing the pan servo angle"""
    mock_pan_servo, _ = mock_hardware_pwms

    servos = Servos(logger=mock_logger, pan_angle=90.0, delta_angle=5.0)
    servos.incr_pan()

    assert servos._pan_angle == 95.0

    mock_pan_servo.change_duty_cycle.assert_called_with(
        servos._angle_to_duty_cycle(95.0)
    )


def test_decr_pan(mock_hardware_pwms, mock_logger):
    """test decrementing the pan servo angle"""
    mock_pan_servo, _ = mock_hardware_pwms

    servos = Servos(logger=mock_logger, pan_angle=90.0, delta_angle=5.0)
    servos.decr_pan()

    assert servos._pan_angle == 85.0

    mock_pan_servo.change_duty_cycle.assert_called_with(
        servos._angle_to_duty_cycle(85.0)
    )


def test_incr_pan_at_max(mock_hardware_pwms, mock_logger):
    """test behaviour of incrementing pan servo when it's already reached it's max angle"""
    mock_pan_servo, _ = mock_hardware_pwms

    servos = Servos(logger=mock_logger, pan_angle=180.0)
    servos.incr_pan()

    # Since it's at max, angle should not change
    assert servos._pan_angle == 180.0
    mock_pan_servo.change_duty_cycle.assert_not_called()


def test_decr_pan_at_min(mock_hardware_pwms, mock_logger):
    """test behaviour of decrementing pan servo when it's already reached it's min angle"""
    mock_pan_servo, _ = mock_hardware_pwms

    servos = Servos(logger=mock_logger, pan_angle=0.0)
    servos.decr_pan()

    # Since it's at max, angle should not change
    assert servos._pan_angle == 0.0
    mock_pan_servo.change_duty_cycle.assert_not_called()


def test_set_tilt_angle(mock_hardware_pwms, mock_logger):
    """test setting the tilt servo angle"""
    _, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger)
    servos.set_tilt_angle(120)

    assert servos._tilt_angle == 120

    mock_tilt_servo.change_duty_cycle.assert_called_with(
        servos._angle_to_duty_cycle(120)
    )


def test_incr_tilt(mock_hardware_pwms, mock_logger):
    """test incrementing the tilt servo angle"""
    _, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger, tilt_angle=90.0, delta_angle=5.0)
    servos.incr_tilt()

    assert servos._tilt_angle == 95.0

    mock_tilt_servo.change_duty_cycle.assert_called_with(
        servos._angle_to_duty_cycle(95.0)
    )


def test_decr_tilt(mock_hardware_pwms, mock_logger):
    """test decrementing the tilt servo angle"""
    _, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger, tilt_angle=90.0, delta_angle=5.0)
    servos.decr_tilt()

    assert servos._tilt_angle == 85.0

    mock_tilt_servo.change_duty_cycle.assert_called_with(
        servos._angle_to_duty_cycle(85.0)
    )


def test_incr_tilt_at_max(mock_hardware_pwms, mock_logger):
    """test behaviour of incrementing tilt servo when it's already reached it's max angle"""
    _, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger, tilt_angle=180.0)
    servos.incr_tilt()

    # Since it's at max, angle should not change
    assert servos._tilt_angle == 180.0
    mock_tilt_servo.change_duty_cycle.assert_not_called()


def test_decr_tilt_at_min(mock_hardware_pwms, mock_logger):
    """test behaviour of decrementing tilt servo when it's already reached it's min angle"""
    _, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger, tilt_angle=0.0)
    servos.decr_tilt()

    # Since it's at min, angle should not change
    assert servos._tilt_angle == 0.0
    mock_tilt_servo.change_duty_cycle.assert_not_called()


def test_home(mock_hardware_pwms, mock_logger):
    """test correct operation of the home function"""
    mock_pan_servo, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger, pan_angle=45.0, tilt_angle=135.0)
    servos.home()

    assert servos._pan_angle == 90.0
    assert servos._tilt_angle == 90.0

    mock_pan_servo.change_duty_cycle.assert_any_call(
        servos._angle_to_duty_cycle(90.0)
    )
    mock_tilt_servo.change_duty_cycle.assert_any_call(
        servos._angle_to_duty_cycle(90.0)
    )


def test_cleanup(mock_hardware_pwms, mock_logger):
    """test that the cleanup function works as expected"""
    mock_pan_servo, mock_tilt_servo = mock_hardware_pwms

    servos = Servos(logger=mock_logger)
    servos._cleanup()

    mock_pan_servo.stop.assert_any_call()
    mock_tilt_servo.stop.assert_any_call()
