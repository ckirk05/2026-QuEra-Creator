from manimlib import *
from collections import defaultdict

RUN_TIME = 0.01


class QuantumCircuitScene(Scene):
    def construct(self):
        # Parameters
        self.n_qubits = 3
        self.circuit = [
            {"type": "H", "qubits": [0], "x_shift": 2},
            {"type": "CNOT", "qubits": [0, 1], "x_shift": 4},
            {"type": "M", "qubits": [0, 1, 2], "x_shift": 6},
        ]

        # Run phases
        self.draw_qubits()
        self.draw_qubit_labels()
        self.draw_and_animate_gates()
        self.animate_qubit_states()
        self.collapse_and_split()
        self.create_qubit_grid()
        self.show_troll_with_bubble()
        self.flash_red_and_replace_qubits()
        list1 = [0, 5, 10]  # first set of qubits
        list2 = [1, 6, 11]
        self.wizard_spell_between_lists(list1, list2)

    # -------------------------
    # Phase 1: Qubit lines
    # -------------------------
    def draw_qubits(self):
        last_gate_x = [0] * self.n_qubits
        for gate in self.circuit:
            for q in gate["qubits"]:
                last_gate_x[q] = max(last_gate_x[q], gate["x_shift"])
        last_gate_x = [x + 1 for x in last_gate_x]  # padding

        self.qubits = VGroup()
        for i in range(self.n_qubits):
            line = Line(LEFT * 5, LEFT * 5 + RIGHT * last_gate_x[i])
            self.qubits.add(line)
        self.qubits.arrange(DOWN, buff=1.5).to_edge(LEFT, buff=1)
        self.play(*[ShowCreation(q) for q in self.qubits], run_time=RUN_TIME)

    # -------------------------
    # Phase 2: Qubit labels
    # -------------------------
    def draw_qubit_labels(self):
        self.labels = VGroup(
            *[
                Text(f"q{i}", font_size=24).next_to(self.qubits[i], LEFT)
                for i in range(self.n_qubits)
            ]
        )
        self.play(*[Write(label) for label in self.labels], run_time=RUN_TIME)

    # -------------------------
    # Phase 3: Gate drawing helpers
    # -------------------------
    def draw_single_gate(self, label, qubit_index, x_shift):
        gate = Square(side_length=0.7, color=BLUE).move_to(
            self.qubits[qubit_index].get_start() + RIGHT * x_shift
        )
        gate_label = Text(label, font_size=24).move_to(gate.get_center())
        return VGroup(gate, gate_label)

    def draw_two_qubit_gate(
        self,
        control_qubit,
        target_qubit,
        x_shift,
        target_symbol="X",
        control_color=RED,
        target_color=BLUE,
    ):
        # Control dot
        control_dot = Dot(radius=0.1, color=control_color).move_to(
            self.qubits[control_qubit].get_start() + RIGHT * x_shift
        )
        # Target square + symbol
        target_square = Square(side_length=0.7, color=target_color).move_to(
            self.qubits[target_qubit].get_start() + RIGHT * x_shift
        )
        target_label = Text(target_symbol, font_size=24).move_to(
            target_square.get_center()
        )
        target_gate = VGroup(target_square, target_label)
        # Connecting line
        line = Line(
            control_dot.get_center(),
            target_square.get_center() - target_square.get_height() / 2 * DOWN,
            color=control_color,
        )
        return control_dot, line, target_gate

    # -------------------------
    # Phase 4: Animate gates
    # -------------------------
    def draw_and_animate_gates(self):
        # Group gates by x_shift for parallel animation
        gates_by_x = defaultdict(list)
        for gate_info in self.circuit:
            gates_by_x[gate_info["x_shift"]].append(gate_info)

        self.gates = VGroup()
        for x_shift, gates in sorted(gates_by_x.items()):
            animations = []
            for gate_info in gates:
                if gate_info["type"] in ["H", "M"]:
                    for q in gate_info["qubits"]:
                        g = self.draw_single_gate(gate_info["type"], q, x_shift)
                        self.gates.add(g)
                        animations.append(FadeIn(g))
                elif gate_info["type"] == "CNOT":
                    control, target = gate_info["qubits"]
                    target_gate, control_dot, line = self.draw_two_qubit_gate(
                        control, target, x_shift, target_symbol="X"
                    )
                    self.gates.add(control_dot, target_gate)
                    animations.extend(
                        [FadeIn(control_dot), FadeIn(target_gate), ShowCreation(line)]
                    )
            self.play(*animations, run_time=RUN_TIME)

    # -------------------------
    # Phase 5: Animate qubit states
    # -------------------------
    def animate_qubit_states(self):
        qubit_dots = VGroup(
            *[Dot(color=YELLOW).move_to(q.get_start()) for q in self.qubits]
        )
        self.play(*[FadeIn(dot) for dot in qubit_dots], run_time=RUN_TIME)
        self.play(
            *[
                dot.animate.move_to(q.get_end())
                for dot, q in zip(qubit_dots, self.qubits)
            ],
            # run_time=3,
            run_time=RUN_TIME,
        )

    def collapse_and_split(
        self, image_path="/Users/antoine/Downloads/neutral_wizard_blue.png"
    ):
        # -------------------------
        # 1. Create middle IMAGE
        # -------------------------
        middle_image = ImageMobject(image_path).move_to(ORIGIN)
        self.add(middle_image)

        # -------------------------
        # 2. Animate all objects scaling down (EXCEPT Camera & Middle Image)
        # -------------------------
        collapse_anims = []

        for obj in self.mobjects:
            # 1. Skip the middle image
            if obj is middle_image:
                continue

            # 2. CRITICAL FIX: Skip the Camera Frame
            # If the camera frame shrinks, it creates a "Zoom In" effect.
            # We check if the object is the camera's frame (if it exists).
            if hasattr(self, "camera") and hasattr(self.camera, "frame"):
                if obj is self.camera.frame:
                    continue

            # Scale down to 0 and fade out
            collapse_anims.append(
                obj.animate.move_to(middle_image.get_center()).scale(0).set_opacity(0)
            )

        # Run the collapse animation
        if collapse_anims:
            self.play(
                self.camera.frame.animate.scale(0.2).move_to(
                    middle_image.get_center() + UP * 0.1
                ),
                *collapse_anims,
                run_time=2.5,
            )

        self.wait(0.5)

        # Clean up: Remove invisible objects (But keep Camera & Middle Image)
        for obj in list(self.mobjects):
            # Don't remove the middle image
            if obj is middle_image:
                continue

            # Don't remove the camera frame
            if (
                hasattr(self, "camera")
                and hasattr(self.camera, "frame")
                and obj is self.camera.frame
            ):
                continue

            self.remove(obj)

        # -------------------------
        # 3. Split into two final IMAGES
        # -------------------------
        offset = 0.5

        self.left_dot = middle_image.copy()
        self.right_dot = middle_image.copy()

        self.add(self.left_dot, self.right_dot)
        self.remove(middle_image)

        self.play(
            self.left_dot.animate.move_to(ORIGIN + LEFT * offset),
            self.right_dot.animate.move_to(ORIGIN + RIGHT * offset),
            run_time=0.5,
        )

    def create_qubit_grid(
        self,
        n_qubits=15,
        rows=3,
        cols=5,
        spacing=1.0,
        image_path="/Users/antoine/Downloads/neutral_wizard_blue.png",
        image_scale=0.5,
    ):
        self.qubit_images = Group()

        # 1. Create the grid objects
        for i in range(n_qubits):
            row = i // cols
            col = i % cols
            x = (col - (cols - 1) / 2) * spacing
            y = ((rows - 1) / 2 - row) * spacing
            pos = np.array([x, y, 0])

            img = ImageMobject(image_path).scale(image_scale).move_to(pos)
            self.qubit_images.add(img)

        # 2. Camera Zoom
        grid_width = (cols - 1) * spacing
        grid_height = (rows - 1) * spacing
        scale_factor = min((grid_width + 2), grid_height)

        self.play(
            self.camera.frame.animate.scale(scale_factor),
            run_time=1,
        )

        # 3. Transform dots to images
        # We use a list of animations so we can add the group at the end safely
        anims = [
            Transform(self.left_dot, self.qubit_images[0]),
            Transform(self.right_dot, self.qubit_images[1]),
        ]

        # Add the rest of the transforms
        for i in range(n_qubits):
            # Skip 0 and 1 because we handled them above manually for left/right dot
            if i > 1:
                # Decide which dot to copy from based on even/odd
                start_obj = (
                    self.left_dot.copy() if i % 2 == 0 else self.right_dot.copy()
                )
                anims.append(
                    Transform(start_obj, self.qubit_images[i], rate_func=smooth)
                )

        self.play(*anims, run_time=2)

        # 4. CRITICAL FIX: Swap the "Transformed Dots" for the actual "Image Group"
        # If you don't do this, the images aren't really there to be manipulated later.
        self.remove(self.left_dot, self.right_dot)
        # Remove any lingering copies from the loop (Manim usually handles this, but let's be safe)
        self.clear()
        self.add(self.qubit_images)

    def show_troll_with_bubble(self):
        # ---------------------------------------------------------
        # THE FIX: Use an Overlay Rectangle instead of set_opacity
        # ---------------------------------------------------------
        # Create a black rectangle that covers the whole camera view
        self.dimmer = FullScreenRectangle(
            fill_color=BLACK,
            fill_opacity=0.8,  # Adjust this: 0.8 is dark, 0.2 is light
            stroke_width=0,
        )

        # Ensure the dimmer is ABOVE the grid but BELOW the troll
        # (Manim adds new objects on top by default)

        self.play(FadeIn(self.dimmer), run_time=RUN_TIME)
        # ---------------------------------------------------------
        # Troll Setup
        # ---------------------------------------------------------
        self.troll = ImageMobject(
            "/Users/antoine/Downloads/neutral_wizard_yellow.png"
        ).scale(0.6)

        # Optional: Position troll
        # troll.move_to(ORIGIN)

        self.text = Text("You shall not pass!", font_size=36, color=BLACK)

        self.bubble = SurroundingRectangle(
            self.text,
            buff=0.1,
            fill_color=WHITE,
            fill_opacity=0,  # Bubble needs to be opaque to read text
            stroke_color=WHITE,
        )

        self.bubble.move_to(
            self.troll.get_center() + np.array([0, 1.0, 0])
        )  # move above troll
        self.text.move_to(self.bubble.get_center())

        # Animate Troll and Bubble appearing ON TOP of the dimmer
        self.play(FadeIn(self.troll, shift=UP), run_time=RUN_TIME)
        self.play(GrowFromCenter(self.bubble), Write(self.text), run_time=RUN_TIME)

        self.wait(2)

    def flash_red_and_replace_qubits(
        self,
        new_image_path="/Users/antoine/Downloads/neutral_wizard_yellow.png",
        image_scale=0.5,
    ):
        # 1️⃣ Remove troll and dimer if they exist
        self.remove(self.troll)
        self.remove(self.dimmer)
        self.remove(self.bubble)
        self.remove(self.text)

        # 2️⃣ Full-screen red flash
        red_flash = FullScreenRectangle(fill_color=RED, fill_opacity=0)
        self.add(red_flash)

        # Animate flash: fade in quickly and fade out
        self.play(red_flash.animate.set_opacity(0.8), run_time=0.15)
        self.play(red_flash.animate.set_opacity(0), run_time=0.15)
        self.remove(red_flash)

        # 3️⃣ Replace all qubit images

        new_qubit_wrappers = Group()  # create new wrappers
        for wrapper in self.qubit_images:
            # Position of the old wrapper
            pos = wrapper.get_center()

            # Create new wrapper with new image
            new_img = ImageMobject(new_image_path).scale(image_scale)
            new_wrapper = Group(new_img).move_to(pos)
            new_wrapper.set_opacity(0)  # start invisible

            new_qubit_wrappers.add(new_wrapper)

        # 4️⃣ Replace old qubits with new ones
        self.remove(self.qubit_images)
        self.add(new_qubit_wrappers)
        self.qubit_images = new_qubit_wrappers

        # 5️⃣ Animate new images appearing
        self.play(
            *[wrapper.animate.set_opacity(1) for wrapper in self.qubit_images],
            run_time=RUN_TIME,
        )

    def wizard_spell_between_lists(
        self, list1, list2, move_offset=np.array([0.5, 0, 0]), run_time=1.5
    ):
        """
        Animate a wizard spell between two lists of qubit indices.
        list1[i] will cast a spell to list2[i].
        Optionally, move list1 qubits by move_offset while casting.
        """
        # 1️⃣ Store original positions for qubits in list1
        orig_pos_list1 = {i: self.qubit_images[i].get_center() for i in list1}

        # 2️⃣ Move list1 qubits by move_offset (optional)
        anims_move = [
            self.qubit_images[i].animate.move_to(
                self.qubit_images[i].get_center() + move_offset
            )
            for i in list1
        ]
        self.play(*anims_move, run_time=run_time)

        # 3️⃣ Cast spells between corresponding qubits in parallel
        # 3️⃣ Cast spells between corresponding qubits in parallel
        spell_lines = []
        anims_appear = []
        anims_pulse = []
        anims_fade = []

        for i, j in zip(list1, list2):
            q1 = self.qubit_images[i]
            q2 = self.qubit_images[j]

            start = q1.get_center()
            end = q2.get_center()

            # Wavy curve for spell
            num_points = 20
            curve_points = [
                start
                + (end - start) * t
                + np.array([0, 0.1 * np.sin(10 * t * np.pi), 0])
                for t in np.linspace(0, 1, num_points)
            ]

            spell_line = VMobject()
            spell_line.set_points_as_corners(curve_points)
            spell_line.set_stroke(color=BLUE, width=3)
            spell_line.set_opacity(1.0)  # start visible
            self.add(spell_line)
            spell_lines.append(spell_line)

            # Prepare animations
            anims_pulse.append(spell_line.animate.set_color(YELLOW).scale(1.2))
            anims_fade.append(spell_line.animate.set_opacity(0.2))

        # Animate all spells pulsing at the same time
        self.play(*anims_pulse, rate_func=there_and_back, run_time=1.5)

        # Animate all spells fading at the same time
        self.play(*anims_fade, run_time=0.5)

        # Remove all spell lines from the scene
        for spell_line in spell_lines:
            self.remove(spell_line)

        # 4️⃣ Small swirl for all qubits
        swirl_anims = []
        for img in self.qubit_images:
            original_pos = img.get_center()
            swirl_path = [
                original_pos + np.array([0.05, 0.05, 0]),
                original_pos + np.array([-0.05, 0.05, 0]),
                original_pos + np.array([-0.05, -0.05, 0]),
                original_pos + np.array([0.05, -0.05, 0]),
                original_pos,
            ]
            for next_pos in swirl_path:
                swirl_anims.append(img.animate.move_to(next_pos))
        self.play(*swirl_anims, run_time=1.5)

        # 5️⃣ Return list1 qubits to original positions
        anims_return = [
            self.qubit_images[i].animate.move_to(pos - move_offset)
            for i, pos in orig_pos_list1.items()
        ]
        self.play(*anims_return, run_time=run_time)

        # def
