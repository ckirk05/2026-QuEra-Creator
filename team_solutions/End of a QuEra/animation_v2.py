from manimlib import *
from collections import defaultdict
import os

RUN_TIME = 0.001


class QuantumCircuitScene(Scene):
    def construct(self):
        # Parameters
        self.n_qubits = 7
        self.circuit = [
            {"type": "-SY", "qubits": [0], "x_shift": 2},
            {"type": "-SY", "qubits": [1], "x_shift": 2},
            {"type": "-SY", "qubits": [2], "x_shift": 2},
            {"type": "-SY", "qubits": [3], "x_shift": 2},
            {"type": "-SY", "qubits": [4], "x_shift": 2},
            {"type": "-SY", "qubits": [5], "x_shift": 2},
            {"type": "CZ", "qubits": [1, 2], "x_shift": 4},
            {"type": "CZ", "qubits": [3, 4], "x_shift": 4},
            {"type": "CZ", "qubits": [5, 6], "x_shift": 4},
            {"type": "SY", "qubits": [6], "x_shift": 6},
            {"type": "CZ", "qubits": [0, 3], "x_shift": 8},
            {"type": "CZ", "qubits": [2, 5], "x_shift": 8},
            {"type": "CZ", "qubits": [4, 6], "x_shift": 8},
            {"type": "SY", "qubits": [2], "x_shift": 10},
            {"type": "SY", "qubits": [3], "x_shift": 10},
            {"type": "SY", "qubits": [4], "x_shift": 10},
            {"type": "SY", "qubits": [5], "x_shift": 10},
            {"type": "SY", "qubits": [6], "x_shift": 10},
            {"type": "CZ", "qubits": [0, 1], "x_shift": 12},
            {"type": "CZ", "qubits": [2, 3], "x_shift": 12},
            {"type": "CZ", "qubits": [4, 5], "x_shift": 12},
            {"type": "SY", "qubits": [1], "x_shift": 14},
            {"type": "SY", "qubits": [2], "x_shift": 14},
            {"type": "SY", "qubits": [4], "x_shift": 14},
            {
                "type": "M",
                "qubits": [0, 1, 2, 3, 4, 5, 6],
                "x_shift": 16,
            },
        ]

        self.qubit_asset_paths = [None] * self.n_qubits  # current file path per qubit
        self.qubit_levels = [0] * self.n_qubits  # current state level per qubit

        # Run phases
        self.draw_qubits()
        self.draw_qubit_labels()
        self.draw_and_animate_gates()
        self.animate_qubit_states()
        self.collapse_and_split()
        self.create_qubit_grid()
        self.execute_circuit_wizard_style()

    def execute_circuit_wizard_style(self):
        # Group gates by x_shift so we animate parallel gates together
        gates_by_x = defaultdict(list)
        for gate_info in self.circuit:
            gates_by_x[gate_info["x_shift"]].append(gate_info)

        for x_shift, gates in sorted(gates_by_x.items()):
            single_qubits = []
            single_ops = []
            two_qubit_pairs = []

            # 1️⃣ Sort gates into single- or two-qubit
            for gate_info in gates:
                gtype = gate_info["type"]
                qubits = gate_info["qubits"]

                if gtype in [
                    "SY",
                    "-SY",
                    "H",
                ]:
                    single_qubits.extend(qubits)
                    single_ops.extend([gtype] * len(qubits))
                elif gtype == "CZ" or gtype == "CNOT":
                    two_qubit_pairs.append(qubits)
                elif gtype == "TROLL":  # optional: special broadcast event
                    self.troll_flash_and_replace_qubits()
                    continue

            # 2️⃣ Apply single-qubit wizard animations
            if single_qubits:
                self.apply_single_qubit_wizard_operations(
                    qubit_indices=single_qubits,
                    operations=single_ops,
                    state_levels=[
                        50 if single_ops[i] == "SY" else -50
                        for i in range(len(single_ops))
                    ],
                    color_names=["blue"] * len(single_qubits),
                    image_scale=0.5,
                )

            # 3️⃣ Apply two-qubit wizard spells
            control, target = [], []
            for pair in two_qubit_pairs:
                control.append(pair[0])
                target.append(pair[1])
            if control and target:
                self.wizard_spell_between_lists(control, target)

            # 4️⃣ Optional small wait between x_shifts
            self.wait(0.3)

        # self.troll_flash_and_replace_qubits()
        # list1 = [2]  # first set of qubits
        # list2 = [3]
        # self.wizard_spell_between_lists(list1, list2)
        # self.apply_single_qubit_wizard_operations(
        #     [0, 2, 5],
        #     ["H", "M", "X"],
        #     state_levels=[25, 50, 75],
        #     color_names=["orange", "blue", "pink"],
        #     image_scale=0.5,
        # )
        # self.show_troll_with_bubble()
        # self.flash_red_and_replace_qubits()
        # list1 = [0, 5, 10]  # first set of qubits
        # list2 = [1, 6, 11]
        # self.wizard_spell_between_lists(list1, list2)

    def draw_qubits(self):
        last_gate_x = [0] * self.n_qubits
        for gate in self.circuit:
            for q in gate["qubits"]:
                last_gate_x[q] = max(last_gate_x[q], gate["x_shift"])
        last_gate_x = [x + 1 for x in last_gate_x]  # padding

        # 1️⃣ Determine total horizontal width and vertical spacing
        total_width = max(last_gate_x) + 1
        scene_height = 8  # approximate scene height
        spacing = scene_height / (self.n_qubits + 1)

        # 2️⃣ Create qubit lines
        self.qubits = VGroup()
        for i in range(self.n_qubits):
            start = LEFT * total_width / 2
            end = start + RIGHT * last_gate_x[i]
            line = Line(start, end)
            self.qubits.add(line)

        # 3️⃣ Arrange vertically with spacing
        self.qubits.arrange(DOWN, buff=spacing).move_to(ORIGIN)

        # 4️⃣ Camera scaling: ensure all qubits and circuit width fit
        scene_width = 14
        camera_width = total_width + 2  # add margin
        camera_height = spacing * self.n_qubits + 2
        scale_factor = min(scene_width / camera_width, scene_height / camera_height)

        self.camera.frame.save_state()
        self.camera.frame.scale(1 / scale_factor)
        self.camera.frame.move_to(ORIGIN)  # center the frame

        self.play(*[ShowCreation(q) for q in self.qubits], run_time=RUN_TIME)

    def draw_qubit_labels(self):
        self.labels = VGroup(
            *[
                Text(f"q{i}", font_size=24).next_to(self.qubits[i], LEFT)
                for i in range(self.n_qubits)
            ]
        )
        self.play(*[Write(label) for label in self.labels], run_time=RUN_TIME)

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

    def draw_and_animate_gates(self):
        # Group gates by x_shift for parallel animation
        gates_by_x = defaultdict(list)
        for gate_info in self.circuit:
            gates_by_x[gate_info["x_shift"]].append(gate_info)

        self.gates = VGroup()
        for x_shift, gates in sorted(gates_by_x.items()):
            animations = []
            for gate_info in gates:
                if gate_info["type"] in ["-SY", "SY", "H", "X", "M"]:
                    for q in gate_info["qubits"]:
                        g = self.draw_single_gate(gate_info["type"], q, x_shift)
                        self.gates.add(g)
                        animations.append(FadeIn(g))
                elif gate_info["type"] == "CNOT" or gate_info["type"] == "CZ":
                    control, target = gate_info["qubits"]
                    target_gate, control_dot, line = self.draw_two_qubit_gate(
                        control,
                        target,
                        x_shift,
                        target_symbol="X" if gate_info["type"] == "CNOT" else "Z",
                    )
                    self.gates.add(control_dot, target_gate)
                    animations.extend(
                        [FadeIn(control_dot), FadeIn(target_gate), ShowCreation(line)]
                    )
            self.play(*animations, run_time=RUN_TIME)

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
        self,
        image_path="/Users/antoine/Developpement/Quera_challenge/endofaquera/handdrawn_assets/blue/blue_0.png",
    ):
        # 1️⃣ Create middle IMAGE at origin
        middle_image = ImageMobject(image_path).move_to(ORIGIN)
        self.add(middle_image)

        # 2️⃣ Animate all qubit-related objects scaling down to middle image
        collapse_anims = []
        for obj in self.mobjects:
            if obj in [middle_image, getattr(self, "camera", None)]:
                continue
            collapse_anims.append(
                obj.animate.move_to(middle_image.get_center()).scale(0).set_opacity(0)
            )

        if collapse_anims:
            self.play(
                self.camera.frame.animate.scale(0.2).move_to(
                    middle_image.get_center() + UP * 0.1
                ),
                *collapse_anims,
                run_time=2.5,
            )

        self.wait(0.5)

        # Remove all objects except middle image and camera frame
        for obj in list(self.mobjects):
            if obj is middle_image or (
                hasattr(self, "camera") and obj is self.camera.frame
            ):
                continue
            self.remove(obj)

        # 3️⃣ Split into two final IMAGES
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
        image_path="/Users/antoine/Developpement/Quera_challenge/endofaquera/handdrawn_assets/blue/blue_0.png",
        image_scale=0.5,
        max_cols=7,
    ):
        n_qubits = self.n_qubits
        self.qubit_images = Group()

        # 1️⃣ Determine columns and rows
        cols = min(n_qubits, max_cols)
        rows = int(np.ceil(n_qubits / cols))

        # 2️⃣ Compute simple spacing in Manim units (1–2 units works well)
        spacing_x = 1
        spacing_y = 1

        # 3️⃣ Create qubit images and center the grid
        for i in range(n_qubits):
            row = i // cols
            col = i % cols
            x = (col - (cols - 1) / 2) * spacing_x
            y = ((rows - 1) / 2 - row) * spacing_y
            pos = np.array([x, y, 0])
            img = ImageMobject(image_path).scale(image_scale).move_to(pos)
            self.qubit_asset_paths[i] = image_path
            self.qubit_images.add(img)

        # 4️⃣ Adjust camera to show entire grid
        grid_width = (cols - 1) * spacing_x + image_scale * 2
        grid_height = (rows - 1) * spacing_y + image_scale * 2

        camera_frame_width = self.camera.frame.get_width()
        camera_frame_height = self.camera.frame.get_height()

        scale_factor = max(
            grid_width / camera_frame_width, grid_height / camera_frame_height
        )
        self.camera.frame.scale(scale_factor)
        self.play(
            self.camera.frame.animate.move_to(ORIGIN),
            run_time=0.5,
        )
        # self.camera.frame.move_to(ORIGIN)

        # 5️⃣ Animate left/right dots transforming into first two images
        anims = [
            Transform(self.left_dot, self.qubit_images[0]),
            Transform(
                self.right_dot,
                self.qubit_images[1] if n_qubits > 1 else self.qubit_images[0],
            ),
        ]
        objects_to_remove = [self.left_dot, self.right_dot]
        for i in range(2, n_qubits):
            start_obj = self.left_dot.copy() if i % 2 == 0 else self.right_dot.copy()
            objects_to_remove.append(start_obj)
            anims.append(Transform(start_obj, self.qubit_images[i], rate_func=smooth))
            self.remove(start_obj)

        self.play(*anims, run_time=2)
        self.remove(*objects_to_remove)

        # 6️⃣ Replace transformed dots with final images
        self.remove(self.left_dot, self.right_dot)
        self.add(self.qubit_images)

    def troll_flash_and_replace_qubits(
        self,
        new_image_path="/Users/antoine/Developpement/Quera_challenge/endofaquera/handdrawn_assets/blue/blue_50.png",
        qubit_image_scale=0.5,
        troll_image_path="/Users/antoine/Developpement/Quera_challenge/endofaquera/handdrawn_assets/extras/idium_dad.png",
        troll_scale=0.6,
        troll_text="You shall not pass!",
    ):
        # -------------------------------
        # 1️⃣ Dim the background
        # -------------------------------
        dimmer = FullScreenRectangle(
            fill_color=BLACK,
            fill_opacity=0.8,
            stroke_width=0,
        )
        self.add(dimmer)

        # -------------------------------
        # 2️⃣ Troll and bubble setup
        # -------------------------------
        troll = ImageMobject(troll_image_path).scale(troll_scale)
        text = Text(troll_text, font_size=36, color=BLACK)
        bubble = SurroundingRectangle(
            text, buff=0.1, fill_color=WHITE, fill_opacity=0, stroke_color=WHITE
        )

        bubble.move_to(troll.get_center() + UP * 1.0)
        text.move_to(bubble.get_center())

        self.add(troll, bubble, text)

        # -------------------------------
        # 3️⃣ Troll appears
        # -------------------------------
        self.play(
            FadeIn(troll, shift=UP),
            GrowFromCenter(bubble),
            Write(text),
            run_time=RUN_TIME,
        )
        self.wait(1)

        # -------------------------------
        # 4️⃣ Flash red and remove troll
        # -------------------------------
        red_flash = FullScreenRectangle(fill_color=RED, fill_opacity=1)
        self.add(red_flash)

        self.play(
            FadeIn(troll, shift=UP),
            GrowFromCenter(bubble),
            Write(text),
            run_time=RUN_TIME,
        )
        self.remove(troll, bubble, text, dimmer, red_flash)
        self.play(red_flash.animate.set_opacity(0), run_time=0.15)

        # -------------------------------
        # 5️⃣ Replace all qubit images
        # -------------------------------
        new_qubit_wrappers = Group()
        for wrapper in self.qubit_images:
            pos = wrapper.get_center()
            new_img = ImageMobject(new_image_path).scale(qubit_image_scale)
            new_wrapper = Group(new_img).move_to(pos).set_opacity(0)
            new_qubit_wrappers.add(new_wrapper)
            self.qubit_asset_paths[self.qubit_images.index(wrapper)] = new_image_path
        for i in range(self.qubit_images.__len__()):
            self.remove(self.qubit_images[i])
        self.add(new_qubit_wrappers)
        self.qubit_images = new_qubit_wrappers

        # -------------------------------
        # 6️⃣ Animate new qubit images appearing
        # -------------------------------
        self.play(
            *[wrapper.animate.set_opacity(1) for wrapper in self.qubit_images],
            run_time=RUN_TIME,
        )

    def wizard_spell_between_lists(
        self,
        list1,
        list2,
        move_offset=np.array([0.5, 0, 0]),
        run_time=1.5,
        state_level=50,
        color_name="orange",
        image_scale=0.5,
    ):
        """
        Animate a wizard spell between two lists of qubit indices.
        list1[i] will cast a spell to list2[i].
        """

        # 1️⃣ Store original positions for qubits in list1
        orig_pos_list1 = {i: self.qubit_images[i].copy().get_center() for i in list1}

        # 2️⃣ Move list1 qubits
        anims_move = [
            self.qubit_images[i].animate.move_to(
                self.qubit_images[j].get_center() - move_offset
            )
            for i, j in zip(list1, list2)
        ]
        self.play(*anims_move, run_time=run_time)

        # 3️⃣ Cast spells
        spell_lines = []
        anims_pulse = []
        anims_fade = []

        for i, j in zip(list1, list2):
            q1 = self.qubit_images[i]
            q2 = self.qubit_images[j]
            self.update_wizard_images(
                [i, j],
                state_level=state_level,
                color_name=color_name,
                image_scale=image_scale,
            )

            start = q1.get_center()
            end = q2.get_center()

            # Wavy spell line
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
            spell_line.set_opacity(1.0)
            self.add(spell_line)
            spell_lines.append(spell_line)

            anims_pulse.append(spell_line.animate.set_color(YELLOW).scale(1.2))
            anims_fade.append(spell_line.animate.set_opacity(0.2))

            # -------------------------
            # Call the separate function here
            # -------------------------

        # Animate spells pulsing
        self.play(*anims_pulse, rate_func=there_and_back, run_time=1.5)
        # Animate spells fading
        self.play(*anims_fade, run_time=0.5)

        # Remove spell lines
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
            self.qubit_images[i].animate.move_to(pos)
            for i, pos in orig_pos_list1.items()
        ]
        self.play(*anims_return, run_time=run_time)

    def update_wizard_images(self, indices, state_level, color_name, image_scale=0.5):
        path_template = "/Users/antoine/Developpement/Quera_challenge/endofaquera/handdrawn_assets/{}/{}_{}.png"

        for i in indices:
            old_img = self.qubit_images[i]  # get the old ImageMobject
            current_color, current_level = self.get_current_color_and_level(i)
            if current_level is not None:
                state_level = current_level
            image_path = path_template.format(color_name, color_name, state_level)
            new_img = (
                ImageMobject(image_path)
                .scale(image_scale)
                .move_to(old_img.get_center())
            )
            self.qubit_asset_paths[i] = image_path

            self.remove(old_img)
            self.qubit_images.submobjects[i] = new_img
            self.add(new_img)

            # Optional color effect
            new_img.set_color(color_name.upper())

    def apply_single_qubit_wizard_operations(
        self,
        qubit_indices,
        operations,
        state_levels=None,
        color_names=None,
        image_scale=0.5,
    ):
        """
        Apply single-qubit wizard operations to multiple qubits **in parallel**.
        Sparks, image replacement, and smile updates happen together.
        """
        if len(qubit_indices) != len(operations):
            raise ValueError("qubit_indices and operations must have the same length")
        if state_levels is None:
            state_levels = [50] * len(qubit_indices)
        if color_names is None:
            color_names = ["orange"] * len(qubit_indices)

        path_template = "/Users/antoine/Developpement/Quera_challenge/endofaquera/handdrawn_assets/{}/{}_{}.png"

        new_images = []
        all_sparks = []

        # 1️⃣ Create all new images and sparks
        for i, op, level, color in zip(
            qubit_indices, operations, state_levels, color_names
        ):
            old_img = self.qubit_images[i]
            current_color, get_current_level = self.get_current_color_and_level(i)
            if current_color is not None:
                color = current_color
            level = level + self.qubit_levels[i]
            if level > 100 or level < -100:
                level = level % 100
            self.qubit_levels[i] = level
            image_path = path_template.format(color, color, abs(level))
            new_img = (
                ImageMobject(image_path)
                .scale(image_scale)
                .move_to(old_img.get_center())
            )
            self.qubit_asset_paths[i] = image_path
            new_img.set_color(color.upper())
            new_images.append((i, old_img, new_img))

            # Sparks
            spark_count = 6
            sparks = VGroup()
            for _ in range(spark_count):
                offset = np.array(
                    [np.random.uniform(-0.15, 0.15), np.random.uniform(-0.15, 0.15), 0]
                )
                spark = Dot(radius=0.05, color=YELLOW).move_to(
                    new_img.get_center() + offset
                )
                sparks.add(spark)
                self.add(spark)
            all_sparks.append(sparks)

        # 3️⃣ Animate all sparks in parallel
        spark_anims = [
            spark.animate.scale(2).set_opacity(0)
            for sparks in all_sparks
            for spark in sparks
        ]

        self.play(*spark_anims, run_time=0.5, rate_func=there_and_back)

        # 2️⃣ Replace all old images at once
        for i, old_img, new_img in new_images:
            self.remove(old_img)
            self.qubit_images.submobjects[i] = new_img
            self.add(new_img)

        # 4️⃣ Remove all sparks
        for sparks in all_sparks:
            for spark in sparks:
                self.remove(spark)

    def create_smile(self, alpha, beta, width=0.5):
        """
        Returns a VMobject representing a smile based on amplitudes alpha, beta.
        alpha, beta are complex amplitudes (can use absolute values if you want).
        """
        amp0 = np.abs(alpha)
        amp1 = np.abs(beta)

        # Smile curvature: more |beta| = bigger smile, more |alpha| = flatter
        curvature = (amp1 - amp0) * 0.4  # tweak factor for visual effect

        # Define smile points relative to origin
        left = np.array([-width / 2, 0, 0])
        right = np.array([width / 2, 0, 0])
        control = np.array([0, curvature, 0])

        smile = VMobject()
        smile.set_points_as_corners([left, control, right])
        smile.set_stroke(width=2, color=YELLOW)
        return smile

    def get_current_color_and_level(self, qubit_index):
        """
        Returns the current color name and state level for the given qubit index
        based on the stored asset path.
        """
        path = self.qubit_asset_paths[qubit_index]
        if path is None:
            return None, None
        # Extract color name and level from the file path
        parts = os.path.basename(path).split("_")
        if len(parts) <= 3:
            color_name = parts[0]
            try:
                state_level = int(parts[1].split(".")[0])  # remove file extension
            except ValueError:
                state_level = None
            return color_name, state_level
        return None, None
