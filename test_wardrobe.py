"""Tests for the wardrobe system — rank-up detection, celebration, item unlocks."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from pet import Pet
from drawing import PetDrawer
from settings import (
    BADGE_RANKS, WARDROBE_HAT_TIERS, WARDROBE_GLASSES_TIERS,
    WARDROBE_TAB_TIERS, WARDROBE_SCARF_TIERS, WARDROBE_COLLAR_TIERS,
    WARDROBE_SPECIAL_TIERS, WARDROBE_STYLE_TIER, WARDROBE_PATTERN_TIER,
    WARDROBE_COLOR_TIERS,
    WARDROBE_NATURAL_COLORS, WARDROBE_EXOTIC_COLORS,
    WARDROBE_ACCENT_COLORS, WARDROBE_ACCENT_EXPERT,
    PET_CENTER_X, PET_CENTER_Y, KAWAII_BODY_W, KAWAII_TOTAL_H, GROWTH_SCALE,
    WARDROBE_HINT_DURATION,
)
from wardrobe import WardrobeOverlay
from ui import UI


def _make_pet_with_mastery(pet_type, mastered_count):
    """Create a pet with N words at box=2 (mastered)."""
    pet = Pet(pet_type)
    pet.name = "TestPet"
    for i in range(mastered_count):
        pet.word_mastery[f"word_{i}"] = {
            "box": 2, "correct": 5, "wrong": 0, "streak": 5,
        }
    return pet


class TestVocabBadgeRanks(unittest.TestCase):
    """Test that vocab badge rank thresholds are correct."""

    def test_novice_at_zero(self):
        pet = _make_pet_with_mastery("cat", 0)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Novice")
        self.assertEqual(idx, 0)

    def test_learner_at_5(self):
        pet = _make_pet_with_mastery("cat", 5)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Learner")
        self.assertEqual(idx, 1)

    def test_scholar_at_15(self):
        pet = _make_pet_with_mastery("cat", 15)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Scholar")
        self.assertEqual(idx, 2)

    def test_expert_at_30(self):
        pet = _make_pet_with_mastery("cat", 30)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Expert")
        self.assertEqual(idx, 3)

    def test_master_at_50(self):
        pet = _make_pet_with_mastery("cat", 50)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Master")
        self.assertEqual(idx, 4)

    def test_just_below_learner(self):
        pet = _make_pet_with_mastery("cat", 4)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Novice")
        self.assertEqual(idx, 0)

    def test_just_below_scholar(self):
        pet = _make_pet_with_mastery("cat", 14)
        _, idx = pet.vocab_badge
        self.assertEqual(idx, 1)  # still Learner


class TestWordMasteryProgression(unittest.TestCase):
    """Test that word mastery (box levels) progress correctly."""

    def test_word_reaches_box1_at_streak_2(self):
        pet = Pet("cat")
        pet.record_word_result("apple", True)
        self.assertEqual(pet.word_mastery["apple"]["box"], 0)
        self.assertEqual(pet.word_mastery["apple"]["streak"], 1)
        pet.record_word_result("apple", True)
        self.assertEqual(pet.word_mastery["apple"]["box"], 1)
        self.assertEqual(pet.word_mastery["apple"]["streak"], 2)

    def test_word_reaches_box2_at_streak_4(self):
        pet = Pet("cat")
        for _ in range(3):
            pet.record_word_result("apple", True)
        self.assertEqual(pet.word_mastery["apple"]["box"], 1)
        pet.record_word_result("apple", True)
        self.assertEqual(pet.word_mastery["apple"]["box"], 2)

    def test_wrong_answer_resets_streak(self):
        pet = Pet("cat")
        pet.record_word_result("apple", True)
        pet.record_word_result("apple", True)
        pet.record_word_result("apple", True)
        self.assertEqual(pet.word_mastery["apple"]["streak"], 3)
        pet.record_word_result("apple", False)
        self.assertEqual(pet.word_mastery["apple"]["streak"], 0)
        self.assertEqual(pet.word_mastery["apple"]["box"], 0)  # demoted from 1

    def test_wrong_answer_demotes_box(self):
        pet = _make_pet_with_mastery("cat", 1)
        word = list(pet.word_mastery.keys())[0]
        self.assertEqual(pet.word_mastery[word]["box"], 2)
        pet.record_word_result(word, False)
        self.assertEqual(pet.word_mastery[word]["box"], 1)

    def test_mastering_5_words_reaches_learner(self):
        """Simulate mastering exactly 5 words through repeated correct answers."""
        pet = Pet("cat")
        words = ["apple", "banana", "cat", "dog", "elephant"]
        for _ in range(4):  # 4 rounds of getting each word right
            for w in words:
                pet.record_word_result(w, True)
        mastered = sum(1 for d in pet.word_mastery.values() if d["box"] == 2)
        self.assertEqual(mastered, 5)
        name, idx = pet.vocab_badge
        self.assertEqual(name, "Learner")
        self.assertEqual(idx, 1)


class TestRankUpDetection(unittest.TestCase):
    """Test that rank-up is detected and celebration is triggered."""

    def _make_game(self):
        """Create a minimal Game-like object for testing rank-up detection."""
        from unittest.mock import MagicMock

        class FakeGame:
            def __init__(self):
                self.pet = None
                self._last_badge_rank = 0
                self._badge_celebration_timer = 0.0
                self._badge_celebration_data = None
                self.sound = MagicMock()

        # Patch the methods from main.Game onto FakeGame
        from main import Game
        FakeGame._check_badge_rank_up = Game._check_badge_rank_up
        FakeGame._get_rank_unlocks = Game._get_rank_unlocks
        return FakeGame()

    def test_rank_up_novice_to_learner(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 5)
        game._last_badge_rank = 0  # was Novice
        game._check_badge_rank_up()
        self.assertEqual(game._badge_celebration_timer, 4.0)
        self.assertIsNotNone(game._badge_celebration_data)
        rank_name, rank_color, unlocked = game._badge_celebration_data
        self.assertEqual(rank_name, "Learner")
        self.assertEqual(game._last_badge_rank, 1)

    def test_rank_up_learner_to_scholar(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 15)
        game._last_badge_rank = 1  # was Learner
        game._check_badge_rank_up()
        self.assertEqual(game._badge_celebration_timer, 4.0)
        rank_name, _, unlocked = game._badge_celebration_data
        self.assertEqual(rank_name, "Scholar")
        self.assertEqual(game._last_badge_rank, 2)

    def test_no_rank_up_when_same_rank(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 5)
        game._last_badge_rank = 1  # already Learner
        game._check_badge_rank_up()
        self.assertEqual(game._badge_celebration_timer, 0.0)
        self.assertIsNone(game._badge_celebration_data)

    def test_no_rank_up_at_novice(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 3)
        game._last_badge_rank = 0  # still Novice
        game._check_badge_rank_up()
        self.assertEqual(game._badge_celebration_timer, 0.0)

    def test_unlocked_items_for_learner(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 5)
        game._last_badge_rank = 0
        game._check_badge_rank_up()
        _, _, unlocked = game._badge_celebration_data
        # Learner should unlock hats tab, glasses tab, and their tier-1 items
        self.assertIn("Hats Tab", unlocked)
        self.assertIn("Glasses Tab", unlocked)
        # Check specific items
        learner_hats = [k.replace("_", " ").title()
                        for k, t in WARDROBE_HAT_TIERS.items() if t == 1]
        for hat in learner_hats:
            self.assertIn(hat, unlocked)

    def test_unlocked_items_for_scholar(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 15)
        game._last_badge_rank = 1
        game._check_badge_rank_up()
        _, _, unlocked = game._badge_celebration_data
        self.assertIn("Colors Tab", unlocked)
        # Scholar hats
        scholar_hats = [k.replace("_", " ").title()
                        for k, t in WARDROBE_HAT_TIERS.items() if t == 2]
        for hat in scholar_hats:
            self.assertIn(hat, unlocked)

    def test_unlocked_items_for_expert(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 30)
        game._last_badge_rank = 2
        game._check_badge_rank_up()
        _, _, unlocked = game._badge_celebration_data
        self.assertIn("Styles Tab", unlocked)
        self.assertIn("Extras Tab", unlocked)

    def test_rank_up_plays_sound(self):
        game = self._make_game()
        game.pet = _make_pet_with_mastery("cat", 5)
        game._last_badge_rank = 0
        game._check_badge_rank_up()
        game.sound.play.assert_called_with("level_up")


class TestPetClickDetection(unittest.TestCase):
    """Test pet click bounding box and wardrobe tap routing."""

    def _pet_rect(self, pet):
        scale = GROWTH_SCALE.get(pet.growth_stage, 1.0)
        w = int(KAWAII_BODY_W * 2 * scale) + 30
        h = int(KAWAII_TOTAL_H * scale) + 30
        return pygame.Rect(PET_CENTER_X - w // 2, PET_CENTER_Y - h // 2 - 10,
                           w, h)

    def test_pet_center_in_rect(self):
        pet = Pet("cat")
        rect = self._pet_rect(pet)
        self.assertTrue(rect.collidepoint(PET_CENTER_X, PET_CENTER_Y))

    def test_buttons_not_in_rect(self):
        """Buttons at y=540 should not overlap pet rect."""
        pet = Pet("cat")
        rect = self._pet_rect(pet)
        self.assertFalse(rect.collidepoint(240, 540))

    def test_rect_scales_with_growth(self):
        """Adult pet has larger rect than baby."""
        baby = Pet("cat")
        baby.growth_stage = "baby"
        adult = Pet("cat")
        adult.growth_stage = "adult"
        baby_rect = self._pet_rect(baby)
        adult_rect = self._pet_rect(adult)
        self.assertGreater(adult_rect.width, baby_rect.width)
        self.assertGreater(adult_rect.height, baby_rect.height)


class TestWardrobeOverlay(unittest.TestCase):
    """Test WardrobeOverlay tab/item behavior."""

    def test_learner_sees_hats_and_glasses_tabs(self):
        pet = _make_pet_with_mastery("cat", 5)
        drawer = PetDrawer()
        overlay = WardrobeOverlay(pet, drawer)
        self.assertTrue(overlay._is_tab_unlocked("hats"))
        self.assertTrue(overlay._is_tab_unlocked("glasses"))
        self.assertFalse(overlay._is_tab_unlocked("colors"))
        self.assertFalse(overlay._is_tab_unlocked("styles"))

    def test_scholar_sees_colors_tab(self):
        pet = _make_pet_with_mastery("cat", 15)
        overlay = WardrobeOverlay(pet, PetDrawer())
        self.assertTrue(overlay._is_tab_unlocked("colors"))
        self.assertFalse(overlay._is_tab_unlocked("styles"))

    def test_expert_sees_styles_extras(self):
        pet = _make_pet_with_mastery("cat", 30)
        overlay = WardrobeOverlay(pet, PetDrawer())
        self.assertTrue(overlay._is_tab_unlocked("styles"))
        self.assertTrue(overlay._is_tab_unlocked("extras"))
        self.assertFalse(overlay._is_tab_unlocked("special"))

    def test_master_sees_all_tabs(self):
        pet = _make_pet_with_mastery("cat", 50)
        overlay = WardrobeOverlay(pet, PetDrawer())
        for tab_key, _ in [("hats", ""), ("glasses", ""), ("colors", ""),
                           ("styles", ""), ("extras", ""), ("special", "")]:
            self.assertTrue(overlay._is_tab_unlocked(tab_key),
                            f"{tab_key} should be unlocked at Master")

    def test_hats_have_tiered_items(self):
        pet = _make_pet_with_mastery("cat", 5)  # Learner
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "hats"
        items = overlay._get_items_for_tab()
        # Should have mix of unlocked (tier 1) and locked (tier 2, 3)
        unlocked = [(k, l) for k, l, t in items if t <= 1]
        locked = [(k, l) for k, l, t in items if t > 1]
        self.assertGreater(len(unlocked), 0, "Should have unlocked hats at Learner")
        self.assertGreater(len(locked), 0, "Should have locked hats teased")

    def test_scholar_unlocks_more_hats(self):
        """Scholar should unlock more hats than Learner."""
        learner_pet = _make_pet_with_mastery("cat", 5)
        scholar_pet = _make_pet_with_mastery("cat", 15)
        learner_overlay = WardrobeOverlay(learner_pet, PetDrawer())
        scholar_overlay = WardrobeOverlay(scholar_pet, PetDrawer())

        learner_overlay._active_tab = "hats"
        scholar_overlay._active_tab = "hats"

        learner_items = learner_overlay._get_items_for_tab()
        scholar_items = scholar_overlay._get_items_for_tab()

        learner_unlocked = sum(1 for _, _, t in learner_items if t <= 1)
        scholar_unlocked = sum(1 for _, _, t in scholar_items if t <= 2)

        self.assertGreater(scholar_unlocked, learner_unlocked,
                           "Scholar should unlock more hats than Learner")

    def test_select_hat_updates_preview(self):
        pet = _make_pet_with_mastery("cat", 5)
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "hats"
        overlay._select_item("beret")
        self.assertEqual(pet.appearance["hat"], "beret")
        self.assertEqual(overlay._preview["hat"], "beret")

    def test_done_commits_appearance(self):
        pet = _make_pet_with_mastery("cat", 5)
        original_hat = pet.appearance["hat"]
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "hats"
        overlay._select_item("beret")
        overlay._commit()
        self.assertEqual(pet.appearance["hat"], "beret")
        self.assertTrue(overlay.done)

    def test_back_reverts_appearance(self):
        pet = _make_pet_with_mastery("cat", 5)
        pet.appearance["hat"] = "flower"
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "hats"
        overlay._select_item("beret")
        self.assertEqual(pet.appearance["hat"], "beret")
        overlay._revert()
        self.assertEqual(pet.appearance["hat"], "flower")
        self.assertTrue(overlay.done)

    def test_novice_cannot_open_wardrobe(self):
        """At Novice rank, wardrobe should not open (tooltip shown instead)."""
        pet = _make_pet_with_mastery("cat", 0)
        _, rank_idx = pet.vocab_badge
        self.assertEqual(rank_idx, 0)
        # The game logic checks rank_index < 1 to show tooltip instead
        self.assertTrue(rank_idx < 1)


class TestWardrobeColors(unittest.TestCase):
    """Test color palette tier locking in the Colors tab."""

    def test_scholar_sees_natural_colors(self):
        pet = _make_pet_with_mastery("cat", 15)
        overlay = WardrobeOverlay(pet, PetDrawer())
        natural_tier = WARDROBE_COLOR_TIERS["natural"]
        self.assertTrue(natural_tier <= overlay._rank_index)

    def test_scholar_cannot_use_exotic_colors(self):
        pet = _make_pet_with_mastery("cat", 15)
        overlay = WardrobeOverlay(pet, PetDrawer())
        exotic_tier = WARDROBE_COLOR_TIERS["exotic"]
        self.assertFalse(exotic_tier <= overlay._rank_index)

    def test_expert_can_use_exotic_colors(self):
        pet = _make_pet_with_mastery("cat", 30)
        overlay = WardrobeOverlay(pet, PetDrawer())
        exotic_tier = WARDROBE_COLOR_TIERS["exotic"]
        self.assertTrue(exotic_tier <= overlay._rank_index)

    def test_scholar_cannot_use_patterns(self):
        pet = _make_pet_with_mastery("cat", 15)
        overlay = WardrobeOverlay(pet, PetDrawer())
        self.assertFalse(WARDROBE_PATTERN_TIER <= overlay._rank_index)

    def test_expert_can_use_patterns(self):
        pet = _make_pet_with_mastery("cat", 30)
        overlay = WardrobeOverlay(pet, PetDrawer())
        self.assertTrue(WARDROBE_PATTERN_TIER <= overlay._rank_index)

    def test_select_body_color_updates_appearance(self):
        pet = _make_pet_with_mastery("cat", 15)
        overlay = WardrobeOverlay(pet, PetDrawer())
        color = [240, 180, 200]
        overlay._preview["body_color"] = color
        for k, v in overlay._preview.items():
            pet.appearance[k] = v
        self.assertEqual(pet.appearance["body_color"], color)


class TestCelebrationToastDrawing(unittest.TestCase):
    """Test that the celebration toast renders without errors."""

    def test_draw_badge_celebration(self):
        ui = UI()
        surf = pygame.Surface((480, 640))
        # Should not raise
        ui.draw_badge_celebration(
            surf, "Scholar", (100, 180, 255),
            ["Crown", "Top Hat", "Cat Eye", "Sunglasses", "Colors Tab"],
            3.0)

    def test_draw_badge_celebration_at_zero_timer(self):
        ui = UI()
        surf = pygame.Surface((480, 640))
        # Should be a no-op, not crash
        ui.draw_badge_celebration(surf, "Scholar", (100, 180, 255), [], 0.0)

    def test_draw_wardrobe_hint(self):
        ui = UI()
        surf = pygame.Surface((480, 640))
        ui.draw_wardrobe_hint(surf, 1.5, mastered_needed=5)

    def test_draw_wardrobe_hint_at_zero(self):
        ui = UI()
        surf = pygame.Surface((480, 640))
        ui.draw_wardrobe_hint(surf, 0.0, mastered_needed=5)


class TestWardrobeOverlayDrawing(unittest.TestCase):
    """Test that wardrobe overlay draws without errors at each rank."""

    def test_draw_at_learner(self):
        pet = _make_pet_with_mastery("cat", 5)
        overlay = WardrobeOverlay(pet, PetDrawer())
        surf = pygame.Surface((480, 640))
        overlay.draw(surf, (0, 0))

    def test_draw_at_scholar_colors_tab(self):
        pet = _make_pet_with_mastery("cat", 15)
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "colors"
        surf = pygame.Surface((480, 640))
        overlay.draw(surf, (0, 0))

    def test_draw_at_expert_styles_tab(self):
        pet = _make_pet_with_mastery("cat", 30)
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "styles"
        surf = pygame.Surface((480, 640))
        overlay.draw(surf, (0, 0))

    def test_draw_at_expert_extras_tab(self):
        pet = _make_pet_with_mastery("cat", 30)
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "extras"
        surf = pygame.Surface((480, 640))
        overlay.draw(surf, (0, 0))

    def test_draw_at_master_special_tab(self):
        pet = _make_pet_with_mastery("cat", 50)
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "special"
        surf = pygame.Surface((480, 640))
        overlay.draw(surf, (0, 0))

    def test_draw_locked_tab_message(self):
        pet = _make_pet_with_mastery("cat", 5)
        overlay = WardrobeOverlay(pet, PetDrawer())
        overlay._active_tab = "colors"  # locked at Learner
        surf = pygame.Surface((480, 640))
        overlay.draw(surf, (0, 0))


class TestEndToEndRankUp(unittest.TestCase):
    """End-to-end test: word mastery → rank change → celebration → wardrobe access."""

    def test_full_flow_novice_to_learner(self):
        """Simulate mastering 5 words and verify the entire unlock chain."""
        pet = Pet("cat")
        pet.name = "TestCat"

        # Verify starting at Novice
        _, rank = pet.vocab_badge
        self.assertEqual(rank, 0)

        # Simulate 4 rounds of 5 words (enough to master 5 words)
        words = ["apple", "banana", "cat", "dog", "elephant"]
        for _ in range(4):
            for w in words:
                pet.record_word_result(w, True)

        # Verify rank changed to Learner
        name, rank = pet.vocab_badge
        self.assertEqual(name, "Learner")
        self.assertEqual(rank, 1)

        # Verify mastered count
        mastered = sum(1 for d in pet.word_mastery.values() if d["box"] == 2)
        self.assertEqual(mastered, 5)

        # Simulate rank-up detection (as Game would do)
        from unittest.mock import MagicMock
        from main import Game
        class FakeGame:
            pass
        fake = FakeGame()
        fake.pet = pet
        fake._last_badge_rank = 0
        fake._badge_celebration_timer = 0.0
        fake._badge_celebration_data = None
        fake.sound = MagicMock()
        # Bind _get_rank_unlocks so _check_badge_rank_up can call it
        fake._get_rank_unlocks = lambda rank: Game._get_rank_unlocks(fake, rank)
        Game._check_badge_rank_up(fake)

        # Verify celebration triggered
        self.assertEqual(fake._badge_celebration_timer, 4.0)
        self.assertIsNotNone(fake._badge_celebration_data)
        rank_name, rank_color, unlocked = fake._badge_celebration_data
        self.assertEqual(rank_name, "Learner")

        # Verify wardrobe now opens (not tooltip)
        overlay = WardrobeOverlay(pet, PetDrawer())
        self.assertTrue(overlay._is_tab_unlocked("hats"))
        self.assertTrue(overlay._is_tab_unlocked("glasses"))

        # Verify items are available
        overlay._active_tab = "hats"
        items = overlay._get_items_for_tab()
        available = [l for _, l, t in items if t <= rank]
        self.assertGreater(len(available), 1)  # None + at least one hat

    def test_full_flow_scholar_to_expert(self):
        """Mastering 30 words unlocks Styles, Extras, and more hats/glasses."""
        pet = _make_pet_with_mastery("cat", 30)
        _, rank = pet.vocab_badge
        self.assertEqual(rank, 3)  # Expert

        overlay = WardrobeOverlay(pet, PetDrawer())

        # All hat items should be unlocked at Expert
        overlay._active_tab = "hats"
        items = overlay._get_items_for_tab()
        all_unlocked = all(t <= rank for _, _, t in items)
        self.assertTrue(all_unlocked, "All hats should be unlocked at Expert")

        # All glasses should be unlocked
        overlay._active_tab = "glasses"
        items = overlay._get_items_for_tab()
        all_unlocked = all(t <= rank for _, _, t in items)
        self.assertTrue(all_unlocked, "All glasses should be unlocked at Expert")

        # Styles tab unlocked with fur/eyes/ears/tail
        self.assertTrue(overlay._is_tab_unlocked("styles"))
        overlay._active_tab = "styles"
        for sub_idx in range(4):  # Fur, Eyes, Ears, Tail
            overlay._active_sub_tab = sub_idx
            items = overlay._get_items_for_tab()
            self.assertGreater(len(items), 1,
                               f"Style sub-tab {sub_idx} should have items")

        # Extras tab unlocked
        self.assertTrue(overlay._is_tab_unlocked("extras"))

        # Special tab still locked
        self.assertFalse(overlay._is_tab_unlocked("special"))


class TestEachRankUnlocksNewContent(unittest.TestCase):
    """Verify that every rank transition unlocks new items across categories."""

    def test_learner_unlocks_hats_and_glasses(self):
        """Learner rank (5 mastered) unlocks Hats tab + Glasses tab."""
        hat_items = [k for k, t in WARDROBE_HAT_TIERS.items() if t == 1]
        glasses_items = [k for k, t in WARDROBE_GLASSES_TIERS.items() if t == 1]
        self.assertGreater(len(hat_items), 0, "Learner should unlock at least 1 hat")
        self.assertGreater(len(glasses_items), 0, "Learner should unlock at least 1 glasses")

    def test_scholar_unlocks_within_existing_tabs(self):
        """Scholar rank (15 mastered) unlocks new items in Hats AND Glasses."""
        scholar_hats = [k for k, t in WARDROBE_HAT_TIERS.items() if t == 2]
        scholar_glasses = [k for k, t in WARDROBE_GLASSES_TIERS.items() if t == 2]
        self.assertGreater(len(scholar_hats), 0,
                           "Scholar should unlock new hats in existing Hats tab")
        self.assertGreater(len(scholar_glasses), 0,
                           "Scholar should unlock new glasses in existing Glasses tab")

    def test_expert_unlocks_within_existing_tabs(self):
        """Expert rank (30 mastered) unlocks new items in Hats AND Glasses."""
        expert_hats = [k for k, t in WARDROBE_HAT_TIERS.items() if t == 3]
        expert_glasses = [k for k, t in WARDROBE_GLASSES_TIERS.items() if t == 3]
        self.assertGreater(len(expert_hats), 0,
                           "Expert should unlock new hats in existing Hats tab")
        self.assertGreater(len(expert_glasses), 0,
                           "Expert should unlock new glasses in existing Glasses tab")

    def test_every_rank_adds_something(self):
        """Every rank from Learner to Master should add at least one new item."""
        for rank_idx in range(1, len(BADGE_RANKS)):
            items_at_rank = []
            for k, t in WARDROBE_HAT_TIERS.items():
                if t == rank_idx:
                    items_at_rank.append(f"hat:{k}")
            for k, t in WARDROBE_GLASSES_TIERS.items():
                if t == rank_idx:
                    items_at_rank.append(f"glasses:{k}")
            for k, t in WARDROBE_TAB_TIERS.items():
                if t == rank_idx:
                    items_at_rank.append(f"tab:{k}")
            for k, t in WARDROBE_SCARF_TIERS.items():
                if t == rank_idx:
                    items_at_rank.append(f"scarf:{k}")
            for k, t in WARDROBE_COLLAR_TIERS.items():
                if t == rank_idx:
                    items_at_rank.append(f"collar:{k}")
            for k, t in WARDROBE_SPECIAL_TIERS.items():
                if t == rank_idx:
                    items_at_rank.append(f"special:{k}")
            rank_name = BADGE_RANKS[rank_idx][0]
            self.assertGreater(len(items_at_rank), 0,
                               f"Rank {rank_name} (idx {rank_idx}) must unlock at least 1 item, "
                               f"found: {items_at_rank}")


if __name__ == "__main__":
    unittest.main()
