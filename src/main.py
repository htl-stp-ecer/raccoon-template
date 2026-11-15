"""
Entry point.

`raccoon run` uploads the project, regenerates hardware/, then executes
`src.main:main` on the Wombat. `Robot().start()` initialises logging, runs the
setup mission, then each mission in order, and finally the shutdown mission.

Keep this file tiny — all behaviour lives in missions/, steps/ and so on.
"""

from src.hardware.robot import Robot

def main():
    robot = Robot()
    robot.start()

if __name__ == "__main__":
    main()
