from manim import *

class MovingCircle(Scene):
    def construct(self):
        # Create a red circle
        circle = Circle(radius=1, color=RED)

        # Initial position
        circle.move_to(LEFT * 3)

        # Animation: Move to the right and scale down
        self.play(
            circle.animate.move_to(RIGHT * 3).scale(0.5),
            run_time=2
        )

        # Pause to keep the final frame
        self.wait(1)