from manim import *
import numpy as np
from pathlib import Path

ASSETS = Path("handdrawn_assets")
WIZARD = ASSETS / "neutral_wizard_orange.png"

# Global slowdown factor
SLOW = 1.1

class ZonedQubitArchitecture(MovingCameraScene):
    def construct(self):
        self.create_zones()
        self.create_storage_qubits(24)  # total qubits: 24
        self.move_qubits_smoothly()
        self.zoom_into_entanglement()
        self.show_entanglement_pairs()
        self.zoom_back_out()
        self.zoom_into_readout()
        self.wait(2)

    # --------------------------------------------------
    # ZONES
    # --------------------------------------------------
    def create_zones(self):
        box_w, box_h = 5, 2.6

        self.storage_box = Rectangle(
            width=box_w, height=box_h, stroke_color=WHITE
        ).move_to(UP * 2.0)

        self.entangle_box = Rectangle(
            width=box_w, height=box_h, stroke_color=BLUE
        ).move_to(LEFT * 3.2 + DOWN * 2.2)

        self.readout_box = Rectangle(
            width=box_w, height=box_h, stroke_color=GREEN
        ).move_to(RIGHT * 3.2 + DOWN * 2.2)

        self.storage_label = Text("Storage", font_size=28).next_to(self.storage_box, UP)
        self.entangle_label = Text("Entanglement", font_size=28).next_to(self.entangle_box, UP)
        self.readout_label = Text("Readout", font_size=28).next_to(self.readout_box, UP)

        animations = [
            Create(self.storage_box),
            Create(self.entangle_box),
            Create(self.readout_box),
            FadeIn(self.storage_label),
            FadeIn(self.entangle_label),
            FadeIn(self.readout_label),
        ]
        if animations:
            self.play(*animations, run_time=2*SLOW)

    # --------------------------------------------------
    # CREATE QUBITS
    # --------------------------------------------------
    def create_storage_qubits(self, n):
        self.qubits = Group()
        rows, cols = 4, 6
        spacing = 0.65
        center = self.storage_box.get_center()

        for i in range(n):
            r, c = divmod(i, cols)
            pos = center + np.array([
                (c - cols / 2 + 0.5) * spacing,
                (rows / 2 - r - 0.5) * spacing,
                0
            ])
            wiz = ImageMobject(WIZARD).scale(0.32).move_to(pos)
            self.qubits.add(wiz)

        if len(self.qubits) > 0:
            self.play(FadeIn(self.qubits), run_time=2*SLOW)

    # --------------------------------------------------
    # SHUTTLING QUBITS
    # --------------------------------------------------
    def move_qubits_smoothly(self):
        self.entangle_qubits = Group()
        self.readout_qubits = Group()
        self.remaining_storage_qubits = Group()

        entangle_count = 8
        readout_count = 8
        storage_count = len(self.qubits) - entangle_count - readout_count

        storage_positions = self.grid_positions(self.storage_box, storage_count)
        entangle_positions = self.grid_positions(self.entangle_box, entangle_count)
        readout_positions = self.grid_positions(self.readout_box, readout_count)

        animations = []

        for i, wiz in enumerate(self.qubits):
            if i < entangle_count:
                self.entangle_qubits.add(wiz)
                animations.append(wiz.animate.move_to(entangle_positions[i]))
            elif i < entangle_count + readout_count:
                self.readout_qubits.add(wiz)
                j = i - entangle_count
                animations.append(wiz.animate.move_to(readout_positions[j]))
            else:
                self.remaining_storage_qubits.add(wiz)
                j = i - entangle_count - readout_count
                animations.append(wiz.animate.move_to(storage_positions[j]))

        if animations:
            self.play(*animations, run_time=4*SLOW, rate_func=smooth)

    # --------------------------------------------------
    # CAMERA: ENTANGLEMENT (sped up 30%)
    # --------------------------------------------------
    def zoom_into_entanglement(self):
        target = self.entangle_box.get_center()
        zoom_width = self.entangle_box.width * 1.4
        self.play(
            self.camera.frame.animate.move_to(target).set(width=zoom_width),
            run_time=3*SLOW*0.7,  # 30% faster
            rate_func=smooth
        )

    # --------------------------------------------------
    # ENTANGLEMENT VISUAL (COLUMN-BASED, sped up 30%)
    # --------------------------------------------------
    def show_entanglement_pairs(self):
        qubits = self.entangle_qubits
        rows, cols = 2, 4  # 8 qubits arranged in 2 rows x 4 columns

        # Step 1: color qubits by column: red, blue, red, blue
        for i, q in enumerate(qubits):
            col = i % cols
            color = RED if col % 2 == 0 else BLUE
            self.play(q.animate.set_color(color), run_time=0.5*SLOW*0.7)

        # Step 2: draw yellow lines row-wise connecting pairs
        lines = []
        for r in range(rows):
            for c in range(0, cols, 2):
                idx1 = r * cols + c
                idx2 = r * cols + c + 1
                if idx2 < len(qubits):
                    line = Line(
                        qubits[idx1].get_center(),
                        qubits[idx2].get_center(),
                        stroke_color=YELLOW,
                        stroke_width=4
                    )
                    lines.append((line, [qubits[idx1], qubits[idx2]]))

        # Step 3: animate lines and turn connected qubits purple
        for line, pair in lines:
            self.play(Create(line), run_time=1.0*SLOW*0.7)
            self.play(*[q.animate.set_color(PURPLE) for q in pair], run_time=0.6*SLOW*0.7)

        self.wait(0.5*SLOW*0.7)

    # --------------------------------------------------
    # CAMERA: ZOOM BACK OUT
    # --------------------------------------------------
    def zoom_back_out(self):
        self.play(
            self.camera.frame.animate.move_to(ORIGIN).set(width=14),
            run_time=3*SLOW,
            rate_func=smooth
        )

    # --------------------------------------------------
    # CAMERA: READOUT WITH HIGHLIGHTED QUBITS
    # --------------------------------------------------
    def zoom_into_readout(self):
        target = self.readout_box.get_center()
        zoom_width = self.readout_box.width * 1.4

        # Zoom camera
        self.play(
            self.camera.frame.animate.move_to(target).set(width=zoom_width),
            run_time=3*SLOW,
            rate_func=smooth
        )

        # Highlight half of the readout qubits
        if hasattr(self, "readout_qubits") and len(self.readout_qubits) > 0:
            highlights = VGroup()
            num_to_measure = max(1, len(self.readout_qubits) // 2)
            for i, q in enumerate(self.readout_qubits):
                if i < num_to_measure:
                    circle = Circle(radius=0.2, stroke_color=YELLOW, stroke_width=3)
                    circle.move_to(q.get_center())
                    highlights.add(circle)

            if len(highlights) > 0:
                self.play(
                    LaggedStartMap(FadeIn, highlights, lag_ratio=0.4),
                    run_time=2.5*SLOW
                )

    # --------------------------------------------------
    # GRID HELPER
    # --------------------------------------------------
    def grid_positions(self, box, n, rows=2, cols=4):
        positions = []
        dx = box.width / (cols + 1)
        dy = box.height / (rows + 1)
        for i in range(n):
            r, c = divmod(i, cols)
            pos = box.get_center() + np.array([
                (c - cols / 2 + 0.5) * dx,
                (rows / 2 - r - 0.5) * dy,
                0
            ])
            positions.append(pos)
        return positions
