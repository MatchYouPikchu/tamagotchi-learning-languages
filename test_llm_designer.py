"""Comprehensive tests for the LLM pet designer pipeline."""

import json
import os
import unittest
from unittest.mock import patch, MagicMock

# Headless pygame setup
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from llm_designer import (
    _validate_appearance, _validate_color, generate_appearance,
    VALID_HATS, VALID_GLASSES, VALID_SCARVES, VALID_COLLARS,
    VALID_SPECIALS, VALID_PATTERNS,
    VALID_FUR_STYLES, VALID_TAIL_STYLES, VALID_EYE_STYLES, VALID_EAR_STYLES,
)
from pet import Pet
from drawing import PetDrawer
from settings import (
    DESIGN_THEMES, PET_CAT, PET_DOG,
    GROWTH_BABY, GROWTH_KID, GROWTH_ADULT,
)


class TestValidateAppearance(unittest.TestCase):
    """B1. Validation tests for _validate_appearance()."""

    def test_valid_complete_input(self):
        data = {
            "body_color": [100, 150, 200],
            "accent_color": [255, 200, 50],
            "pattern": "spots",
            "pattern_color": [80, 80, 80],
            "hat": "crown",
            "glasses": "round",
            "scarf": "rainbow",
            "collar": "bell",
            "special": "sparkle_eyes",
            "fur_style": "fluffy",
            "tail_style": "curly",
            "eye_style": "big",
            "ear_style": "round",
            "suggested_name": "Whiskers",
            "flavor_text": "A royal feline",
        }
        result = _validate_appearance(data)
        self.assertEqual(result["body_color"], [100, 150, 200])
        self.assertEqual(result["accent_color"], [255, 200, 50])
        self.assertEqual(result["pattern"], "spots")
        self.assertEqual(result["pattern_color"], [80, 80, 80])
        self.assertEqual(result["hat"], "crown")
        self.assertEqual(result["glasses"], "round")
        self.assertEqual(result["scarf"], "rainbow")
        self.assertEqual(result["collar"], "bell")
        self.assertEqual(result["special"], "sparkle_eyes")
        self.assertEqual(result["fur_style"], "fluffy")
        self.assertEqual(result["tail_style"], "curly")
        self.assertEqual(result["eye_style"], "big")
        self.assertEqual(result["ear_style"], "round")
        self.assertEqual(result["suggested_name"], "Whiskers")
        self.assertEqual(result["flavor_text"], "A royal feline")

    def test_invalid_hat_defaults_to_none(self):
        result = _validate_appearance({"hat": "sombrero"})
        self.assertIsNone(result["hat"])

    def test_invalid_glasses_defaults_to_none(self):
        result = _validate_appearance({"glasses": "vr_headset"})
        self.assertIsNone(result["glasses"])

    def test_invalid_scarf_defaults_to_none(self):
        result = _validate_appearance({"scarf": "pink"})
        self.assertIsNone(result["scarf"])

    def test_invalid_collar_defaults_to_none(self):
        result = _validate_appearance({"collar": "spiked"})
        self.assertIsNone(result["collar"])

    def test_invalid_special_defaults_to_none(self):
        result = _validate_appearance({"special": "laser_eyes"})
        self.assertIsNone(result["special"])

    def test_invalid_fur_style_defaults_to_none(self):
        result = _validate_appearance({"fur_style": "bald"})
        self.assertIsNone(result["fur_style"])

    def test_invalid_tail_style_defaults_to_none(self):
        result = _validate_appearance({"tail_style": "prehensile"})
        self.assertIsNone(result["tail_style"])

    def test_invalid_eye_style_defaults_to_none(self):
        result = _validate_appearance({"eye_style": "laser"})
        self.assertIsNone(result["eye_style"])

    def test_invalid_ear_style_defaults_to_none(self):
        result = _validate_appearance({"ear_style": "elven"})
        self.assertIsNone(result["ear_style"])

    def test_out_of_range_rgb_clamped(self):
        result = _validate_appearance({"body_color": [300, -10, 128]})
        self.assertEqual(result["body_color"], [255, 0, 128])

    def test_non_list_color_falls_back(self):
        result = _validate_appearance({"body_color": "red"})
        self.assertEqual(result["body_color"], [200, 160, 80])  # default

    def test_missing_fields_get_defaults(self):
        result = _validate_appearance({})
        self.assertEqual(result["body_color"], [200, 160, 80])
        self.assertIsNone(result["accent_color"])
        self.assertEqual(result["pattern"], "solid")
        self.assertIsNone(result["pattern_color"])
        self.assertIsNone(result["hat"])
        self.assertIsNone(result["glasses"])
        self.assertIsNone(result["scarf"])
        self.assertIsNone(result["collar"])
        self.assertIsNone(result["special"])
        self.assertIsNone(result["fur_style"])
        self.assertIsNone(result["tail_style"])
        self.assertIsNone(result["eye_style"])
        self.assertIsNone(result["ear_style"])
        self.assertEqual(result["suggested_name"], "")
        self.assertEqual(result["flavor_text"], "")

    def test_extra_unknown_fields_ignored(self):
        result = _validate_appearance({"wings": "dragon", "hat": "crown"})
        self.assertEqual(result["hat"], "crown")
        self.assertNotIn("wings", result)

    def test_wrong_type_int_for_hat(self):
        result = _validate_appearance({"hat": 42})
        self.assertIsNone(result["hat"])

    def test_wrong_type_list_for_pattern(self):
        result = _validate_appearance({"pattern": [1, 2, 3]})
        self.assertEqual(result["pattern"], "solid")

    def test_suggested_name_truncated(self):
        result = _validate_appearance({"suggested_name": "A" * 50})
        self.assertEqual(len(result["suggested_name"]), 20)

    def test_flavor_text_truncated(self):
        result = _validate_appearance({"flavor_text": "B" * 100})
        self.assertEqual(len(result["flavor_text"]), 60)

    def test_pattern_color_nulled_when_solid(self):
        result = _validate_appearance({
            "pattern": "solid",
            "pattern_color": [255, 0, 0],
        })
        self.assertIsNone(result["pattern_color"])

    def test_pattern_color_kept_when_spots(self):
        result = _validate_appearance({
            "pattern": "spots",
            "pattern_color": [255, 0, 0],
        })
        self.assertEqual(result["pattern_color"], [255, 0, 0])

    def test_pattern_color_kept_when_stripes(self):
        result = _validate_appearance({
            "pattern": "stripes",
            "pattern_color": [0, 255, 0],
        })
        self.assertEqual(result["pattern_color"], [0, 255, 0])

    def test_validate_color_helper(self):
        self.assertEqual(_validate_color([100, 200, 50]), [100, 200, 50])
        self.assertIsNone(_validate_color("red"))
        self.assertIsNone(_validate_color([100, 200]))
        self.assertEqual(_validate_color([999, -5, 128]), [255, 0, 128])
        self.assertIsNone(_validate_color(None))


class TestSchemaRender(unittest.TestCase):
    """B2. Render coverage tests — every valid option renders without crash."""

    @classmethod
    def setUpClass(cls):
        cls.surface = pygame.Surface((480, 640))
        cls.drawer = PetDrawer()

    def _make_pet(self, pet_type, **appearance_overrides):
        p = Pet(pet_type)
        p.appearance["body_color"] = [200, 200, 200]
        for k, v in appearance_overrides.items():
            p.appearance[k] = v
        return p

    def _render(self, pet):
        self.drawer.draw(self.surface, pet)

    def test_every_hat_renders_cat(self):
        for hat in VALID_HATS:
            with self.subTest(hat=hat):
                self._render(self._make_pet(PET_CAT, hat=hat))

    def test_every_hat_renders_dog(self):
        for hat in VALID_HATS:
            with self.subTest(hat=hat):
                self._render(self._make_pet(PET_DOG, hat=hat))

    def test_every_glasses_renders(self):
        for g in VALID_GLASSES:
            with self.subTest(glasses=g):
                self._render(self._make_pet(PET_CAT, glasses=g))

    def test_every_scarf_renders(self):
        for sc in VALID_SCARVES:
            with self.subTest(scarf=sc):
                self._render(self._make_pet(PET_CAT, scarf=sc))

    def test_every_collar_renders(self):
        for c in VALID_COLLARS:
            with self.subTest(collar=c):
                self._render(self._make_pet(PET_DOG, collar=c))

    def test_every_special_renders(self):
        for sp in VALID_SPECIALS:
            with self.subTest(special=sp):
                self._render(self._make_pet(PET_CAT, special=sp))

    def test_every_pattern_renders(self):
        for pat in VALID_PATTERNS:
            with self.subTest(pattern=pat):
                pc = [100, 100, 100] if pat != "solid" else None
                self._render(self._make_pet(PET_CAT, pattern=pat, pattern_color=pc))

    def test_every_fur_style_renders_cat(self):
        for fs in VALID_FUR_STYLES:
            with self.subTest(fur_style=fs):
                self._render(self._make_pet(PET_CAT, fur_style=fs))

    def test_every_fur_style_renders_dog(self):
        for fs in VALID_FUR_STYLES:
            with self.subTest(fur_style=fs):
                self._render(self._make_pet(PET_DOG, fur_style=fs))

    def test_every_tail_style_renders_cat(self):
        for ts in VALID_TAIL_STYLES:
            with self.subTest(tail_style=ts):
                self._render(self._make_pet(PET_CAT, tail_style=ts))

    def test_every_tail_style_renders_dog(self):
        for ts in VALID_TAIL_STYLES:
            with self.subTest(tail_style=ts):
                self._render(self._make_pet(PET_DOG, tail_style=ts))

    def test_every_eye_style_renders_cat(self):
        for es in VALID_EYE_STYLES:
            with self.subTest(eye_style=es):
                self._render(self._make_pet(PET_CAT, eye_style=es))

    def test_every_eye_style_renders_dog(self):
        for es in VALID_EYE_STYLES:
            with self.subTest(eye_style=es):
                self._render(self._make_pet(PET_DOG, eye_style=es))

    def test_every_ear_style_renders_cat(self):
        for ear in VALID_EAR_STYLES:
            with self.subTest(ear_style=ear):
                self._render(self._make_pet(PET_CAT, ear_style=ear))

    def test_every_ear_style_renders_dog(self):
        for ear in VALID_EAR_STYLES:
            with self.subTest(ear_style=ear):
                self._render(self._make_pet(PET_DOG, ear_style=ear))

    def test_all_accessories_combined(self):
        for pt in [PET_CAT, PET_DOG]:
            with self.subTest(pet_type=pt):
                p = self._make_pet(pt,
                    hat="crown", glasses="round", scarf="rainbow",
                    collar="bell", special="sparkle_eyes",
                    pattern="spots", pattern_color=[100, 100, 100],
                    fur_style="fluffy", tail_style="ribbon",
                    eye_style="big", ear_style="round",
                )
                self._render(p)

    def test_all_stages_all_types(self):
        for stage in [GROWTH_BABY, GROWTH_KID, GROWTH_ADULT]:
            for pt in [PET_CAT, PET_DOG]:
                with self.subTest(stage=stage, pet_type=pt):
                    p = self._make_pet(pt,
                        hat="beret", fur_style="spiky",
                        tail_style="long", eye_style="sparkly",
                        ear_style="big",
                    )
                    p.growth_stage = stage
                    self._render(p)


class TestGenerateAppearance(unittest.TestCase):
    """B3. LLM response parsing tests."""

    def _mock_response(self, text):
        """Create a mock Anthropic response."""
        mock_content = MagicMock()
        mock_content.text = text
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        return mock_response

    def _setup_mock_anthropic(self, response_text=None, side_effect=None):
        """Set up a mock anthropic module in sys.modules and return the mock client."""
        import sys
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        if side_effect:
            mock_client.messages.create.side_effect = side_effect
        elif response_text is not None:
            mock_client.messages.create.return_value = self._mock_response(response_text)
        sys.modules["anthropic"] = mock_anthropic
        return mock_client, mock_anthropic

    def tearDown(self):
        import sys
        sys.modules.pop("anthropic", None)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_valid_json_response(self):
        data = {
            "body_color": [200, 100, 150],
            "hat": "crown",
            "pattern": "solid",
            "fur_style": "fluffy",
        }
        self._setup_mock_anthropic(json.dumps(data))

        result = generate_appearance("cat", "a pink royal cat")
        self.assertIsNotNone(result)
        self.assertEqual(result["body_color"], [200, 100, 150])
        self.assertEqual(result["hat"], "crown")
        self.assertEqual(result["fur_style"], "fluffy")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_markdown_fenced_json(self):
        data = {"body_color": [100, 200, 100], "hat": "beret"}
        fenced = f"```json\n{json.dumps(data)}\n```"
        self._setup_mock_anthropic(fenced)

        result = generate_appearance("dog", "a green dog")
        self.assertIsNotNone(result)
        self.assertEqual(result["body_color"], [100, 200, 100])
        self.assertEqual(result["hat"], "beret")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_malformed_json_returns_none(self):
        self._setup_mock_anthropic("not json at all {{{")

        result = generate_appearance("cat", "a cat")
        self.assertIsNone(result)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_api_exception_returns_none(self):
        self._setup_mock_anthropic(side_effect=Exception("API error"))

        result = generate_appearance("cat", "a cat")
        self.assertIsNone(result)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_returns_none(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        result = generate_appearance("cat", "a cat")
        self.assertIsNone(result)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_conversation_history_passed(self):
        data = {"body_color": [200, 200, 200]}
        mock_client, _ = self._setup_mock_anthropic(json.dumps(data))

        history = [
            {"role": "user", "content": "make it blue"},
            {"role": "assistant", "content": "ok"},
        ]
        generate_appearance("cat", "now add a hat", conversation_history=history)

        call_args = mock_client.messages.create.call_args
        messages = call_args[1]["messages"]
        # History messages + the new one
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["content"], "make it blue")
        self.assertEqual(messages[1]["content"], "ok")


class TestDesignThemes(unittest.TestCase):
    """B4. Theme tests."""

    @classmethod
    def setUpClass(cls):
        cls.surface = pygame.Surface((480, 640))
        cls.drawer = PetDrawer()

    def test_all_themes_render(self):
        for name, theme in DESIGN_THEMES.items():
            for pt in [PET_CAT, PET_DOG]:
                with self.subTest(theme=name, pet_type=pt):
                    p = Pet(pt)
                    for k, v in theme.items():
                        if k in p.appearance:
                            p.appearance[k] = v
                    self.drawer.draw(self.surface, p)

    def test_all_theme_keys_are_valid(self):
        valid_keys = set(Pet("cat").appearance.keys())
        for name, theme in DESIGN_THEMES.items():
            for key in theme:
                with self.subTest(theme=name, key=key):
                    self.assertIn(key, valid_keys)

    def test_all_theme_values_valid(self):
        valid_sets = {
            "hat": VALID_HATS,
            "glasses": VALID_GLASSES,
            "scarf": VALID_SCARVES,
            "collar": VALID_COLLARS,
            "special": VALID_SPECIALS,
            "pattern": VALID_PATTERNS,
            "fur_style": VALID_FUR_STYLES,
            "tail_style": VALID_TAIL_STYLES,
            "eye_style": VALID_EYE_STYLES,
            "ear_style": VALID_EAR_STYLES,
        }
        for name, theme in DESIGN_THEMES.items():
            for key, value in theme.items():
                if key in valid_sets:
                    with self.subTest(theme=name, key=key, value=value):
                        self.assertIn(value, valid_sets[key])


class TestBackwardCompat(unittest.TestCase):
    """B5. Backward compatibility tests."""

    @classmethod
    def setUpClass(cls):
        cls.surface = pygame.Surface((480, 640))
        cls.drawer = PetDrawer()

    def test_old_save_no_appearance(self):
        """Old save with no appearance key at all."""
        data = {
            "pet_type": "cat",
            "name": "OldCat",
            "hunger": 80,
            "happiness": 80,
            "energy": 80,
            "cleanliness": 80,
        }
        pet = Pet.from_dict(data)
        # Should have all default appearance values
        self.assertIsNone(pet.appearance["body_color"])
        self.assertEqual(pet.appearance["pattern"], "solid")
        self.assertIsNone(pet.appearance["hat"])
        self.assertIsNone(pet.appearance["fur_style"])
        self.assertIsNone(pet.appearance["tail_style"])
        self.assertIsNone(pet.appearance["eye_style"])
        self.assertIsNone(pet.appearance["ear_style"])

    def test_old_save_partial_appearance(self):
        """Old save with only original appearance keys (no new fields)."""
        data = {
            "pet_type": "dog",
            "name": "OldDog",
            "appearance": {
                "body_color": [255, 200, 100],
                "accent_color": None,
                "pattern": "spots",
                "pattern_color": [100, 100, 100],
                "hat": "crown",
                "glasses": None,
                "scarf": None,
                "collar": None,
                "special": None,
            },
        }
        pet = Pet.from_dict(data)
        self.assertEqual(pet.appearance["body_color"], [255, 200, 100])
        self.assertEqual(pet.appearance["hat"], "crown")
        # New fields should be None (defaults)
        self.assertIsNone(pet.appearance["fur_style"])
        self.assertIsNone(pet.appearance["tail_style"])
        self.assertIsNone(pet.appearance["eye_style"])
        self.assertIsNone(pet.appearance["ear_style"])

    def test_new_save_roundtrip(self):
        """New save with all fields should roundtrip correctly."""
        pet = Pet("cat", "TestCat")
        pet.appearance["body_color"] = [100, 200, 150]
        pet.appearance["fur_style"] = "fluffy"
        pet.appearance["tail_style"] = "ribbon"
        pet.appearance["eye_style"] = "sparkly"
        pet.appearance["ear_style"] = "round"
        pet.appearance["hat"] = "crown"

        data = pet.to_dict()
        restored = Pet.from_dict(data)

        self.assertEqual(restored.appearance["body_color"], [100, 200, 150])
        self.assertEqual(restored.appearance["fur_style"], "fluffy")
        self.assertEqual(restored.appearance["tail_style"], "ribbon")
        self.assertEqual(restored.appearance["eye_style"], "sparkly")
        self.assertEqual(restored.appearance["ear_style"], "round")
        self.assertEqual(restored.appearance["hat"], "crown")

    def test_old_save_renders_without_crash(self):
        """Old save data should render correctly with defaults."""
        data = {
            "pet_type": "cat",
            "name": "OldCat",
            "appearance": {
                "body_color": [200, 150, 100],
                "accent_color": None,
                "pattern": "solid",
                "pattern_color": None,
                "hat": "beret",
                "glasses": None,
                "scarf": None,
                "collar": None,
                "special": None,
            },
        }
        pet = Pet.from_dict(data)
        self.drawer.draw(self.surface, pet)  # Should not crash


class TestPartialValidation(unittest.TestCase):
    """Tests for partial=True mode in _validate_appearance()."""

    def test_partial_only_fur_style(self):
        """Partial mode with only fur_style returns only that key."""
        result = _validate_appearance({"fur_style": "mohawk"}, partial=True)
        self.assertEqual(result, {"fur_style": "mohawk"})

    def test_partial_body_color_and_hat(self):
        """Partial mode with two fields returns only those two."""
        result = _validate_appearance(
            {"body_color": [0, 0, 255], "hat": "crown"}, partial=True)
        self.assertEqual(result["body_color"], [0, 0, 255])
        self.assertEqual(result["hat"], "crown")
        self.assertNotIn("fur_style", result)
        self.assertNotIn("pattern", result)
        self.assertNotIn("suggested_name", result)

    def test_partial_invalid_value_defaults_to_none(self):
        """Partial mode with invalid value still includes the field as None."""
        result = _validate_appearance({"hat": "sombrero"}, partial=True)
        self.assertIn("hat", result)
        self.assertIsNone(result["hat"])

    def test_full_mode_returns_all_fields(self):
        """Full mode (default) still returns all fields as before."""
        result = _validate_appearance({"fur_style": "mohawk"})
        self.assertIn("body_color", result)
        self.assertIn("hat", result)
        self.assertIn("glasses", result)
        self.assertIn("pattern", result)
        self.assertIn("suggested_name", result)
        self.assertIn("flavor_text", result)
        self.assertEqual(result["fur_style"], "mohawk")

    def test_partial_empty_data_returns_empty(self):
        """Empty data + partial → empty result."""
        result = _validate_appearance({}, partial=True)
        self.assertEqual(result, {})

    def test_partial_pattern_color_nulled_when_solid(self):
        """Partial mode: pattern_color nulled if pattern is solid."""
        result = _validate_appearance(
            {"pattern": "solid", "pattern_color": [255, 0, 0]}, partial=True)
        self.assertEqual(result["pattern"], "solid")
        self.assertIsNone(result["pattern_color"])

    def test_partial_suggested_name_only(self):
        """Partial mode with only suggested_name."""
        result = _validate_appearance(
            {"suggested_name": "Spike"}, partial=True)
        self.assertEqual(result, {"suggested_name": "Spike"})

    def test_partial_eye_style_valid(self):
        """Partial mode with valid eye_style."""
        result = _validate_appearance(
            {"eye_style": "sparkly"}, partial=True)
        self.assertEqual(result, {"eye_style": "sparkly"})


class TestCurrentAppearanceContext(unittest.TestCase):
    """Tests for current_appearance parameter in generate_appearance()."""

    def _mock_response(self, text):
        mock_content = MagicMock()
        mock_content.text = text
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        return mock_response

    def _setup_mock_anthropic(self, response_text):
        import sys
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.return_value = self._mock_response(response_text)
        sys.modules["anthropic"] = mock_anthropic
        return mock_client

    def tearDown(self):
        import sys
        sys.modules.pop("anthropic", None)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_current_appearance_included_in_message(self):
        """When current_appearance is provided, it appears in the user message."""
        data = {"fur_style": "mohawk"}
        mock_client = self._setup_mock_anthropic(json.dumps(data))

        current = {"body_color": [0, 0, 255], "hat": "crown", "fur_style": None}
        generate_appearance("cat", "add mohawk hair",
                            current_appearance=current)

        call_args = mock_client.messages.create.call_args
        user_msg = call_args[1]["messages"][-1]["content"]
        self.assertIn("Current appearance:", user_msg)
        self.assertIn('"body_color"', user_msg)
        self.assertIn('"hat"', user_msg)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_no_current_appearance_no_context(self):
        """Without current_appearance, no context in message (backward compat)."""
        data = {"body_color": [200, 200, 200]}
        mock_client = self._setup_mock_anthropic(json.dumps(data))

        generate_appearance("cat", "a gray cat")

        call_args = mock_client.messages.create.call_args
        user_msg = call_args[1]["messages"][-1]["content"]
        self.assertNotIn("Current appearance:", user_msg)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_current_appearance_filters_none_values(self):
        """None values in current_appearance are filtered from context."""
        data = {"hat": "beret"}
        mock_client = self._setup_mock_anthropic(json.dumps(data))

        current = {"body_color": [255, 0, 0], "hat": None, "glasses": None}
        generate_appearance("dog", "add beret", current_appearance=current)

        call_args = mock_client.messages.create.call_args
        user_msg = call_args[1]["messages"][-1]["content"]
        self.assertIn("body_color", user_msg)
        self.assertNotIn('"hat"', user_msg)  # None filtered out
        self.assertNotIn('"glasses"', user_msg)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_current_appearance_uses_partial_validation(self):
        """Result with current_appearance uses partial validation."""
        # LLM returns only fur_style
        data = {"fur_style": "mohawk"}
        self._setup_mock_anthropic(json.dumps(data))

        current = {"body_color": [0, 0, 255], "hat": "crown"}
        result = generate_appearance("cat", "add mohawk",
                                     current_appearance=current)

        self.assertIsNotNone(result)
        self.assertEqual(result["fur_style"], "mohawk")
        # Partial mode: body_color and hat should NOT be in result
        self.assertNotIn("body_color", result)
        self.assertNotIn("hat", result)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_no_current_appearance_uses_full_validation(self):
        """Without current_appearance, full validation returns all keys."""
        data = {"fur_style": "mohawk"}
        self._setup_mock_anthropic(json.dumps(data))

        result = generate_appearance("cat", "design a punk cat")

        self.assertIsNotNone(result)
        self.assertEqual(result["fur_style"], "mohawk")
        # Full mode: all keys present
        self.assertIn("body_color", result)
        self.assertIn("hat", result)


if __name__ == "__main__":
    unittest.main()
