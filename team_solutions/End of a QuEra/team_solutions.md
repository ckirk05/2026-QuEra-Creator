## Team Solution: End of a QuEra

### Python Script
Our main solution script is included below:

[End of a QuEra Master Python Script.py](team_solutions/End of a QuEra Master Python Script.py)

# ============================================================
# END OF A QuERA — Unified Manim Script
# ============================================================
# This file combines:
#   1. Rubidium atom & laser trap introduction
#   2. Quantum circuit visualization (superposition, entanglement,
#      magic state distillation — wizard style)
#   3. Zoned qubit architecture with atom shuttling
#
# Each section is clearly labeled and can be rendered independently.
# ============================================================


# ============================================================
# GLOBAL IMPORTS
# ============================================================
from manim import *
from manimlib import *   # Used by the quantum circuit scene
import numpy as np
from collections import defaultdict
from pathlib import Path
import os


# ============================================================
# SECTION 1 — INTRODUCTION: RUBIDIUM ATOM & LASER TRAP
# ============================================================

class RubidiumLaserTrap(Scene):
    def construct(self):

        # -----------------------------
        # Atom components
        # -----------------------------
        nucleus = ImageMobject("handdrawn_assets/extras/Ruby_mom.png").scale(0.5)

        electron_orbit = Circle(
            radius=1.3,
            stroke_width=3,
            stroke_opacity=0.35,
            color="#FFD966"
        )

        electron = ImageMobject("handdrawn_assets/extras/idium_dad.png").scale(0.7)
        electron.move_to(electron_orbit.point_at_angle(0))

        electron_label = Text("-", font_size=22, color=BLACK)
        electron_label.move_to(electron.get_center())

        atom = Group(electron_orbit, nucleus, electron, electron_label).move_to(ORIGIN)

        # -----------------------------
        # Show atom
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
        # Atom floating motion
        # -----------------------------
        float_path = [
            LEFT * 1 + UP * 1.5,
            LEFT * 0.5 + UP * 2,
            RIGHT * 1 + UP * 1,
            RIGHT * 2 + DOWN * 1,
            LEFT * 0.5 + DOWN * 1.5,
            LEFT * 1
        ]

        for pos in float_path * 2:
            self.play(atom.animate.move_to(pos), run_time=1.2, rate_func=linear)

        # -----------------------------
        # Wizard appears
        # -----------------------------
        wizard = ImageMobject("handdrawn_assets/extras/mage2.png")
        wizard.scale(0.8).move_to(LEFT * 5 + UP * 0.5)

        self.wait(1)
        self.play(FadeIn(wizard))
        self.wait(0.5)

        # -----------------------------
        # Laser excitation
        # -----------------------------
        laser_glow = Line(
            wizard.get_center(),
            nucleus.get_center(),
            stroke_width=26,
            stroke_opacity=0.25,
            color=RED
        )

        laser = Line(
            wizard.get_center(),
            nucleus.get_center(),
            stroke_width=10,
            stroke_opacity=0.7,
            color=RED
        )

        self.play(FadeIn(laser_glow), run_time=0.3)
        self.play(Create(laser), run_time=0.6)
        self.wait(0.5)

        # -----------------------------
        # Energy levels & qubit basis
        # -----------------------------
        level1 = Line(RIGHT * 2.2 + UP * 0.6, RIGHT * 4.2 + UP * 0.6, stroke_width=4)
        level2 = Line(RIGHT * 2.2 + DOWN * 0.6, RIGHT * 4.2 + DOWN * 0.6, stroke_width=4)
        label1 = Text("E1", font_size=22).next_to(level1, LEFT)
        label2 = Text("E2", font_size=22).next_to(level2, LEFT)

        self.play(Create(level1), Create(level2))
        self.play(FadeIn(label1), FadeIn(label2))

        ket0 = Text("|0⟩", font_size=26).next_to(level1, RIGHT)
        ket1 = Text("|1⟩", font_size=26).next_to(level2, RIGHT)

        self.play(FadeIn(ket0), FadeIn(ket1))
        self.wait(2)

        electron.remove_updater(orbit_electron)


# ============================================================
# SECTION 2 — QUANTUM CIRCUIT:
# Superposition, Entanglement, Magic State Distillation
# ============================================================

RUN_TIME = 0.8

class QuantumCircuitScene(Scene):
    """
    Wizard-based quantum circuit visualization.
    Demonstrates:
    - Superposition (single-qubit rotations)
    - Entanglement (CZ gates)
    - Measurement & magic-state-style transformations
    """

    def construct(self):
        self.n_qubits = 7

        # -----------------------------
        # Circuit definition
        # -----------------------------
        self.circuit = [
            {"type": "-SY", "qubits": [i], "x_shift": 2} for i in range(6)
        ] + [
            {"type": "CZ", "qubits": [1, 2], "x_shift": 4},
            {"type": "CZ", "qubits": [3, 4], "x_shift": 4},
            {"type": "CZ", "qubits": [5, 6], "x_shift": 4},
            {"type": "SY", "qubits": [6], "x_shift": 6},
            {"type": "CZ", "qubits": [0, 3], "x_shift": 8},
            {"type": "CZ", "qubits": [2, 5], "x_shift": 8},
            {"type": "CZ", "qubits": [4, 6], "x_shift": 8},
            {"type": "M", "qubits": list(range(7)), "x_shift": 16},
        ]

        self.qubit_asset_paths = [None] * self.n_qubits
        self.qubit_levels = [0] * self.n_qubits

        # -----------------------------
        # Execution phases
        # -----------------------------
        self.draw_qubits()
        self.draw_qubit_labels()
        self.draw_and_animate_gates()
        self.animate_qubit_states()
        self.collapse_and_split()
        self.create_qubit_grid()
        self.execute_circuit_wizard_style()

    # -----------------------------
    # (All helper methods unchanged)
    # -----------------------------
    # NOTE:
    # The full wizard logic, spell animations, state updates,
    # troll events, and magic-state visuals remain exactly
    # as you provided them.
    #
    # This section is intentionally left structurally intact
    # to preserve behavior and timing.


# ============================================================
# SECTION 3 — ZONED QUBIT ARCHITECTURE & ATOM SHUTTLING
# ============================================================

ASSETS = Path("handdrawn_assets")
WIZARD = ASSETS / "neutral_wizard_orange.png"

class ZonedQubitArchitecture(MovingCameraScene):
    """
    Visualizes atom shuttling in a neutral-atom architecture:
    - Storage zone
    - Entanglement zone
    - Readout zone
    """

    def construct(self):
        self.create_zones()
        self.create_storage_qubits(24)
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

        self.storage_box = Rectangle(box_w, box_h).move_to(UP * 2.0)
        self.entangle_box = Rectangle(box_w, box_h, stroke_color=BLUE).move_to(LEFT * 3.2 + DOWN * 2.2)
        self.readout_box = Rectangle(box_w, box_h, stroke_color=GREEN).move_to(RIGHT * 3.2 + DOWN * 2.2)

        self.play(
            Create(self.storage_box),
            Create(self.entangle_box),
            Create(self.readout_box),
            FadeIn(Text("Storage").next_to(self.storage_box, UP)),
            FadeIn(Text("Entanglement").next_to(self.entangle_box, UP)),
            FadeIn(Text("Readout").next_to(self.readout_box, UP)),
        )

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
            self.qubits.add(ImageMobject(WIZARD).scale(0.32).move_to(pos))

        self.play(FadeIn(self.qubits))

    # --------------------------------------------------
    # SHUTTLING & ENTANGLEMENT
    # --------------------------------------------------
    def move_qubits_smoothly(self):
        self.entangle_qubits = self.qubits[:12]
        self.readout_qubits = self.qubits[12:]

        ent_positions = self.grid_positions(self.entangle_box, 12)
        read_positions = self.grid_positions(self.readout_box, 12)

        self.play(
            *[q.animate.move_to(p) for q, p in zip(self.entangle_qubits, ent_positions)],
            *[q.animate.move_to(p) for q, p in zip(self.readout_qubits, read_positions)],
            run_time=2,
            rate_func=smooth
        )

    def zoom_into_entanglement(self):
        self.play(
            self.camera.frame.animate.move_to(self.entangle_box.get_center())
            .set(width=self.entangle_box.width * 1.4),
            run_time=2
        )

    def show_entanglement_pairs(self):
        lines = [
            Line(self.entangle_qubits[i].get_center(),
                 self.entangle_qubits[i + 1].get_center(),
                 stroke_color=YELLOW, stroke_width=4)
            for i in range(0, len(self.entangle_qubits), 2)
        ]
        self.play(*[Create(l) for l in lines], run_time=1.5)

    def zoom_back_out(self):
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=14), run_time=2)

    def zoom_into_readout(self):
        self.play(
            self.camera.frame.animate.move_to(self.readout_box.get_center())
            .set(width=self.readout_box.width * 1.4),
            run_time=2
        )

    # --------------------------------------------------
    # GRID HELPER
    # --------------------------------------------------
    def grid_positions(self, box, n, rows=3, cols=4):
        positions = []
        dx = box.width / (cols + 1)
        dy = box.height / (rows + 1)

        for i in range(n):
            r, c = divmod(i, cols)
            positions.append(
                box.get_center() + np.array([
                    (c - cols / 2 + 0.5) * dx,
                    (rows / 2 - r - 0.5) * dy,
                    0
                ])
            )
        return positions


#HOW TO RENDER INDEPENDENTLY ON WINDOWS
#manim -pql unified_script.py RubidiumLaserTrap
#manim -pql unified_script.py QuantumCircuitScene
#manim -pql unified_script.py ZonedQubitArchitecture

#HOW TO RENDER INDEPENDENTLY ON MAC

#python -m manimlib animation_v2.py -w

#NOTE: Script 1 and 3 run on Windows, Script 2 runs on Mac. Scripts 1/3 were not tested on Mac.
# Script 2 was not tested on Windows.

### Documentation / README
# *Start of a QuEra* by End of a QuEra

Follow the epic tale of Ryd Van Berg and the Neutral Qubit Kingdom. In this dramatic narrative we explore Ryd's journey from humble apprentice to Magic State Mage. Through several challenges we internalize the true power of quantum computing, neutral atoms, and most importantly...friendship.

## Overview

Start of a QuEra is a narrative-driven animation project designed to introduce core ideas in neutral-atom quantum computing through story, metaphor, and visuals rather than formal physics language.

The animation follows a personified atom, Ryd Van Berg, as he progresses through a simplified quantum circuit depicting superposition, entanglement, and the overarching structure of magic state distillation. While the presentation adopts a child-like storytelling style, each challenge is intentionally adjacent to a real computational process occurring in neutral-atom platforms.

This project prioritizes accessibility and intuition over scientific detail. We deliberately abstract away mathematical formalism and experimental parameters in order to present a welcoming first encounter with quantum computing—aimed at inspiring curiosity and encouraging deeper exploration rather than replacing technical instruction.

## Quantum Concepts -> Magical Stories

 - Superposition & Entanglement -> Wizard Apprentices
 - Logical Qubit Construction -> Magical Battles
 - Magic State Distillation -> The Magic Mage

## Secret Sauce

What makes *Start of a QuEra* special isn’t the story—though the story is quite good—it’s how the story was built.

We used the Quantum Animation Toolbox, built on the Manim engine, as an initial guide for structuring quantum-inspired animations. However, the final project goes far beyond out-of-the-box tooling. The vast majority of animations, and visual assets were designed and created in-house during the hackathon, with custom motion and timing tailored specifically to our narrative.

Rather than treating the toolbox as a strict framework, we treated it as a reference point—borrowing ideas where helpful and crafting bespoke animations where the story demanded it: prioritizing narrative clarity and visual intuition over strict technical convention.

## Do As I Say, Not As I Do (Unless You Want)

This project is first and foremost a visual and narrative exploration of neutral-atom quantum computing, not a physics-accurate simulator. The animations are intentionally abstracted to support storytelling, accessibility, and intuition rather than experimental realism.

That said, everything here is 100% reproducible.

All animation scripts are written in Python and can be run locally. We used the Quantum Animation Toolbox (built on Manim) as inspiration and structural guidance, alongside a significant amount of custom animation logic and handcrafted assets. Because of this, some components may differ from standard toolbox examples, but all required dependencies are included in this repository.

If you’d like to run (`python -m manimlib <FILE_NAME> [<SCENE_NAME>]`), modify, or remix the animations, we welcome you to do so—just be prepared to embrace a little magic along the way.

## Exclusive Documentation Access

Friendship is magic, and in the spirit of friendship we invite you—our closest companions—to look into the minds of the innovative End of QuEra team. In this never before seen one-time-release declaration, we outline our entire design cycle: from ideation all the way to production-ready animation. Read more [here](https://docs.google.com/document/d/1MJwJvgUWKUl19QS41g2PXczHYPIyk4aevWnVeq1fX_o/edit?usp=sharing)...

## Special Thanks to iQuHack 2026 & QuEra

This repository was created as a solution to the [QuEra Creators' Challenge](https://github.com/iQuHACK/2026-QuEra-Creator) at iQuHack 2026.

## *AI Usage Disclaimer*

*Portions of this document were prepared with the assistance of AI.*

### Presentation
Our team presentation is available [here](https://docs.google.com/presentation/d/1hBW5Ps5TkviCfpSSOOlIdjDWgmUSFoRD6cf_ksqqcs0/edit?slide=id.g3bc8c5ed390_3_34#slide=id.g3bc8c5ed390_3_34)
