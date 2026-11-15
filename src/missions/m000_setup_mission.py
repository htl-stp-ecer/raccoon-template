from raccoon import *
from src.hardware.defs import Defs
from src.mission_params import MissionParams

class M000SetupMission(SetupMission):
    """
    Runs ONCE before the match — this is where you prepare, not perform.

    Good things to do in setup:
      - Home every servo to a known position.
      - Ask for any table-side parameters (MissionParams).
      - Calibrate the line sensors and drive distance.
      - Wait for the light-start (or a button in dev mode).

    The setup timer is the tournament's pre-match window. We pause it while the
    human is still positioning the robot and resume it once calibration begins,
    so slow human steps don't eat into the budget.
    """

    # How long the pre-match setup window is, in seconds.
    setup_time = 120

    # Sets the calibration distance (in cm).
    calibration_distance_cm = 50

    def sequence(self) -> Sequential:
        return seq([
            # Freeze the setup countdown while the operator gets set up.
            pause_setup_timer(),

            # Everything below is calibration — skipped by using a run config with no-calibrate enabled
            # (i.e. when no_calibrate is set) so you can iterate without re-running it.
            run_unless_no_calibrate(
                seq([
                    wait_for_button(
                        "Calibration\n\n" +
                        f"The robot will now drive {calibration_distance_cm}cm. Place it so it has enough room to do that.\n" +
                        "If IR sensors are present, make sure that in the 50cm driving path, every IR sensor passes" +
                        "over at least one black line so that the IR sensors can properly calibrate."
                    ),

                    # Resume the countdown: real setup work starts now.
                    start_setup_timer(),

                    # Lock the current IMU heading as 0° so the calibration drive
                    # is straight and every later turn_to_heading is relative to it.
                    mark_heading_reference(),

                    # Drive forward while sampling the two front IR sensors. The
                    # collected black/white readings become the "default" IR set,
                    # and the drive distance calibrates the FORWARD axis.
                    # ---
                    # There's two versions here: one where you only calibrate distance, and one where you also
                    # calibrate the IR sensors at the same time – use #1 when no IR sensors are present, and
                    # use #2 if IR sensors are present. You also need to uncomment `require_ir_sets` in the
                    # calibration gate if using #2.
                    # -- #1 --
                    collect_drive(
                        drive_forward(calibration_distance_cm),
                    ),
                    # -- #2 --
                    # collect_drive(
                    #     collect_ir_set(
                    #         drive_forward(calibration_distance_cm),
                    #         set_name="default",
                    #         sensors=[
                    #             Defs.front_left_ir_sensor,
                    #             Defs.front_right_ir_sensor,
                    #         ],
                    #     ),
                    # ),

                    # Finalize the accumulated setup-calibration evidence exactly once.
                    # Refuse to continue unless calibration actually produced the
                    # data we need. Fails loudly here instead of misbehaving mid-match.
                    # ---
                    # → Uncomment the `require_ir_sets` line if you also have IR sensors to calibrate
                    calibration_gate(
                        require_axes=[CalibrationAxis.FORWARD],
                        # require_ir_sets=["default"],
                    ),
                ]),
            ),

            # After setup returns, the runtime automatically waits for the start
            # signal: the light-start sensor in a real match, or the button in
            # dev mode / when no light sensor is configured.
        ])
