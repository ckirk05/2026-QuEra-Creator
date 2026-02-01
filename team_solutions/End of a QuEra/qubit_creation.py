from manim import *
import numpy as np

class RubidiumLaserTrap(Scene):
    def construct(self):

        # -----------------------------
        # Atom components
        # -----------------------------
        nucleus = ImageMobject("handdrawn_assets/extras/Ruby_mom.png")
        nucleus.scale(0.5)

        electron_orbit = Circle(
            radius=1.3,
            stroke_width=3,
            stroke_opacity=0.35,
            color="#FFD966"
        )

        electron = ImageMobject("handdrawn_assets/extras/idium_dad.png")
        electron.scale(0.7)
        electron.move_to(electron_orbit.point_at_angle(0))

        electron_label = Text("-", font_size=22, color=BLACK)
        electron_label.move_to(electron.get_center())

        atom = Group(
            electron_orbit,
            nucleus,
            electron,
            electron_label
        )
        atom.move_to(ORIGIN)

        # -----------------------------
        # Show atom first
        # -----------------------------
        self.play(FadeIn(atom))
        self.wait(0.5)

        # -----------------------------
        # Electron orbit updater
        # -----------------------------
        def orbit_electron(mob, dt):
            orbit_electron.angle += dt * 2.5
            mob.move_to(electron_orbit.point_at_angle(orbit_electron.angle))
            electron_label.move_to(mob.get_center())
        orbit_electron.angle = 0
        electron.add_updater(orbit_electron)

        # -----------------------------
        # Atom floating motion (adjusted path to avoid wizard)
        # -----------------------------
        float_path = [
            LEFT*1 + UP*1.5,
            LEFT*0.5 + UP*2,
            RIGHT*1 + UP*1,
            RIGHT*2 + DOWN*1,
            LEFT*0.5 + DOWN*1.5,
            LEFT*1
        ]

        for pos in float_path * 2:  # repeat path twice
            self.play(atom.animate.move_to(pos), run_time=1.2, rate_func=linear)

        # -----------------------------
        # Wizard appears 1 second before laser
        # -----------------------------
        wizard = ImageMobject("handdrawn_assets/extras/mage2.png")
        wizard.scale(0.8)
        wizard.move_to(LEFT * 5 + UP * 0.5)

        self.wait(1)
        self.play(FadeIn(wizard))
        self.wait(0.5)

        # -----------------------------
        # Laser from wizard to nucleus center (stationary)
        # -----------------------------
        laser_glow = Line(
            start=wizard.get_center(),
            end=nucleus.get_center(),  # laser aimed at nucleus
            stroke_width=26,
            stroke_opacity=0.25,
            color=RED
        )

        laser = Line(
            start=wizard.get_center(),
            end=nucleus.get_center(),  # laser aimed at nucleus
            stroke_width=10,
            stroke_opacity=0.7,
            color=RED
        )

        self.play(FadeIn(laser_glow), run_time=0.3)
        self.play(Create(laser), run_time=0.6)
        self.wait(0.5)

        # -----------------------------
        # Energy levels
        # -----------------------------
        level1 = Line(
            start=RIGHT*2.2 + UP*0.6,
            end=RIGHT*4.2 + UP*0.6,
            stroke_width=4,
            color=WHITE
        )
        level2 = Line(
            start=RIGHT*2.2 + DOWN*0.6,
            end=RIGHT*4.2 + DOWN*0.6,
            stroke_width=4,
            color=WHITE
        )
        label1 = Text("E1", font_size=22).next_to(level1, LEFT, buff=0.3)
        label2 = Text("E2", font_size=22).next_to(level2, LEFT, buff=0.3)

        self.play(Create(level1), Create(level2))
        self.play(FadeIn(label1), FadeIn(label2))

        # -----------------------------
        # Qubit basis states
        # -----------------------------
        self.wait(1)
        ket0 = Text("|0⟩", font_size=26).next_to(level1, RIGHT, buff=0.4)
        ket1 = Text("|1⟩", font_size=26).next_to(level2, RIGHT, buff=0.4)
        self.play(FadeIn(ket0), FadeIn(ket1))
        self.wait(2)

        # -----------------------------
        # Cleanup
        # -----------------------------
        electron.remove_updater(orbit_electron)
