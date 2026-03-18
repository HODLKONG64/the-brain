import importlib.util
import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_module(filename, module_name, overrides=None):
    """Load a hyphen-named Python module from the repo root."""
    path = os.path.join(BASE_DIR, filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if overrides:
        for attr, value in overrides.items():
            setattr(mod, attr, value)
    return mod


class EmergentStorytellingSystemTests(unittest.TestCase):
    def test_emergent_storytelling(self):
        mod = _load_module("emergent-storytelling-system.py", "emergent_storytelling_system")

        updates = [
            {"category": "fishing-real", "content": "Dawn carp session at the reservoir"},
            {"category": "gkdata-real", "content": "GKniftyHEADS NFT mint opens today"},
        ]
        hooks = mod.find_emergent_hooks(updates, {"block": "morning"})
        self.assertIsInstance(hooks, list)
        # fishing-real + gkdata-real pair should produce at least one hook
        self.assertGreater(len(hooks), 0)
        self.assertIsInstance(hooks[0], str)

        # Empty updates returns empty list
        self.assertEqual(mod.find_emergent_hooks([], {}), [])


class LoreFusionEngineTests(unittest.TestCase):
    def test_lore_fusion(self):
        mod = _load_module("lore-fusion-engine.py", "lore_fusion_engine")

        updates = [
            {"category": "fishing-real", "content": "Morning carp session"},
            {"category": "rave-real", "content": "Underground warehouse rave"},
        ]
        emergent_hooks = ["The lake and the dancefloor — two poles of the same life."]
        result = mod.fuse_lore_context(updates, {"block": "morning"}, emergent_hooks)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

        # Empty updates returns a string (not raises)
        empty_result = mod.fuse_lore_context([], {}, [])
        self.assertIsInstance(empty_result, str)


class DialogueGeneratorTests(unittest.TestCase):
    def test_dialogue_generation(self):
        mod = _load_module("dialogue-generator.py", "dialogue_generator")

        result = mod.get_npc_dialogue_context({"block": "morning"}, {})
        self.assertIsInstance(result, str)
        # Should return a non-empty string with dialogue context
        self.assertGreater(len(result), 0)


class SentimentAnalyzerTests(unittest.TestCase):
    def test_sentiment_analysis(self):
        tmpdir = tempfile.mkdtemp()
        history_file = os.path.join(tmpdir, "sentiment-history.json")
        mod = _load_module(
            "sentiment-analyzer.py",
            "sentiment_analyzer",
            overrides={"HISTORY_FILE": history_file},
        )

        positive_text = "Beautiful morning. Caught a massive carp — amazing session, love it."
        sentiment = mod.analyze_sentiment(positive_text)
        self.assertIn(sentiment, {"positive", "negative", "neutral"})
        self.assertEqual(sentiment, "positive")

        negative_text = "Missed everything. Cold, grey, blank day. Nothing worked. Tired."
        sentiment2 = mod.analyze_sentiment(negative_text)
        self.assertEqual(sentiment2, "negative")

        direction = mod.get_sentiment_direction([positive_text])
        self.assertIn(direction, {"needs_positive", "needs_variety", "needs_depth", "balanced"})


class StyleTransferEngineTests(unittest.TestCase):
    def test_style_transfer(self):
        mod = _load_module("style-transfer-engine.py", "style_transfer_engine")

        telegram_hints = mod.get_style_hints("telegram")
        self.assertIsInstance(telegram_hints, str)
        self.assertIn("TELEGRAM", telegram_hints.upper())

        wiki_hints = mod.get_style_hints("wiki")
        self.assertIn("WIKI", wiki_hints.upper())

        # Unknown platform falls back to default
        unknown_hints = mod.get_style_hints("unknown_platform")
        self.assertIsInstance(unknown_hints, str)
        self.assertGreater(len(unknown_hints), 0)


class NarrativeTensionCurveTests(unittest.TestCase):
    def test_narrative_tension(self):
        tmpdir = tempfile.mkdtemp()
        tension_file = os.path.join(tmpdir, "tension-state.json")
        mod = _load_module(
            "narrative-tension-curve.py",
            "narrative_tension_curve",
            overrides={"TENSION_FILE": tension_file},
        )

        hint = mod.get_tension_hint({"block": "morning"}, {})
        self.assertIsInstance(hint, str)
        self.assertGreater(len(hint), 0)
        self.assertIn("TENSION", hint.upper())

        # Night block should increase tension
        hint_night = mod.get_tension_hint({"block": "night"}, {})
        self.assertIsInstance(hint_night, str)
        self.assertIn("TENSION", hint_night.upper())


class MetaNarrativeLayerTests(unittest.TestCase):
    def test_meta_narrative(self):
        mod = _load_module("meta-narrative-layer.py", "meta_narrative_layer")

        # Reset the counter to a known state so we can reliably trigger a hint
        mod._call_counter[0] = mod.META_FREQUENCY - 1

        hint = mod.get_meta_hints({"block": "morning"}, {"mood": "thoughtful"})
        self.assertIsInstance(hint, str)
        # On the META_FREQUENCY-th call, a hint should be returned
        self.assertGreater(len(hint), 0)

        # Between trigger calls, empty string is returned
        hint2 = mod.get_meta_hints({"block": "morning"}, {"mood": "happy"})
        self.assertIsInstance(hint2, str)


class NarrativeInterpolationEngineTests(unittest.TestCase):
    def test_narrative_interpolation(self):
        mod = _load_module(
            "narrative-interpolation-engine.py", "narrative_interpolation_engine"
        )

        filler = mod.get_gap_filler(
            "Morning session at the lake, dawn light, cast out early.",
            "Afternoon in the studio, paint still wet from earlier.",
        )
        self.assertIsInstance(filler, str)
        self.assertGreater(len(filler), 0)

        # Same-time context may return empty or minimal filler
        filler2 = mod.get_gap_filler("Morning walk", "Morning coffee")
        self.assertIsInstance(filler2, str)


class CausalNarrativeWeavingTests(unittest.TestCase):
    def test_causal_narrative_weaving(self):
        mod = _load_module("causal-narrative-weaving.py", "causal_narrative_weaving")

        updates = [
            {"category": "fishing-real", "content": "Dawn carp caught after temperature drop"},
            {"category": "gkdata-real", "content": "NFT floor price spiked after whale buy"},
        ]
        causal_model = "CAUSAL MODEL: fishing + dawn → feeding window. NFT + whale → price spike."
        hints = mod.get_causal_narrative_hints(updates, {"block": "morning"}, causal_model)
        self.assertIsInstance(hints, str)
        self.assertGreater(len(hints), 0)

        # Empty updates returns a string (not raises)
        empty_hints = mod.get_causal_narrative_hints([], {}, "")
        self.assertIsInstance(empty_hints, str)


class CrossMediaUniverseEngineTests(unittest.TestCase):
    def test_cross_media_universe(self):
        tmpdir = tempfile.mkdtemp()
        universe_file = os.path.join(tmpdir, "universe-state.json")
        mod = _load_module(
            "cross-media-universe-engine.py",
            "cross_media_universe_engine",
            overrides={"UNIVERSE_FILE": universe_file},
        )

        # Reset counter to trigger a hint
        mod._call_counter[0] = mod.UNIVERSE_FREQUENCY - 1

        hint = mod.get_universe_hints({"block": "evening"}, [])
        self.assertIsInstance(hint, str)
        # On the UNIVERSE_FREQUENCY-th call, a hint should be returned
        self.assertGreater(len(hint), 0)

        # Between trigger calls, empty string is returned
        hint2 = mod.get_universe_hints({"block": "morning"}, [])
        self.assertIsInstance(hint2, str)


if __name__ == '__main__':
    unittest.main()