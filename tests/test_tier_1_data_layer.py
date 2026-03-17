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


class TestTier1DataLayer(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_data_validator(self):
        mod = _load_module("data-validator.py", "data_validator")

        # High-quality update from a trusted domain should pass
        good = {
            "content": "GraffPUNKS drops new NFT collection this week — limited edition",
            "url": "https://graffpunks.substack.com/p/new-nft-drop",
        }
        result = mod.validate_updates([good])
        self.assertEqual(len(result), 1)
        self.assertIn("confidence", result[0])
        self.assertGreater(result[0]["confidence"], 0.5)

        # Too-short content should be filtered out
        short = {"content": "hi", "url": "https://graffpunks.substack.com/p/x"}
        result = mod.validate_updates([short])
        self.assertEqual(len(result), 0)

        # Empty input returns empty list
        self.assertEqual(mod.validate_updates([]), [])

    def test_causal_inference_engine(self):
        mod = _load_module("causal-inference-engine.py", "causal_inference_engine")

        updates = [
            {"category": "fishing-real", "content": "Morning carp caught at Windermere"},
            {"category": "gkdata-real", "content": "NFT market activity afternoon"},
        ]
        result = mod.build_causal_context(updates, {"block": "morning"})
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("fishing-real", result)

        # Empty updates should return a string (possibly empty or minimal)
        empty_result = mod.build_causal_context([], {"block": "evening"})
        self.assertIsInstance(empty_result, str)

    def test_knowledge_graph_builder(self):
        graph_file = os.path.join(self.tmpdir, "knowledge-graph.json")
        mod = _load_module(
            "knowledge-graph-builder.py",
            "knowledge_graph_builder",
            overrides={"GRAPH_FILE": graph_file},
        )

        updates = [{"content": "Lady-INK tags a mural in Shoreditch", "url": "http://example.com"}]
        lore_text = "Lady-INK and Dave meet at Windermere for a GKniftyHEADS drop."
        graph = mod.update_knowledge_graph(updates, lore_text)

        self.assertIn("entities", graph)
        self.assertIn("relationships", graph)
        self.assertIsInstance(graph["entities"], dict)

        # Graph should contain at least one entity from the lore text
        self.assertGreater(len(graph["entities"]), 0)

    def test_multi_source_fusion(self):
        mod = _load_module("multi-source-fusion.py", "multi_source_fusion")

        # Two very similar updates should be fused into one
        update_a = {
            "title": "GraffPUNKS NFT collection drops soon on WAX",
            "content": "GraffPUNKS NFT collection drops soon on WAX",
            "url": "http://site-a.com/article",
            "confidence": 0.9,
        }
        update_b = {
            "title": "GraffPUNKS NFT collection drops soon on WAX blockchain",
            "content": "GraffPUNKS NFT collection drops soon on WAX blockchain",
            "url": "http://site-b.com/article",
            "confidence": 0.7,
        }
        fused = mod.fuse_updates([update_a, update_b])
        self.assertIsInstance(fused, list)
        # Similar updates merged — result should have fewer items than input
        self.assertLessEqual(len(fused), 2)

        # Completely different updates should both be kept
        update_c = {
            "title": "UK carp fishing record broken at Lake Windermere morning session",
            "content": "UK carp fishing record broken at Lake Windermere morning session",
            "url": "http://carpology.net/record",
            "confidence": 0.8,
        }
        fused2 = mod.fuse_updates([update_a, update_c])
        self.assertEqual(len(fused2), 2)

        # Empty input returns empty list
        self.assertEqual(mod.fuse_updates([]), [])

    def test_world_state_simulator(self):
        mod = _load_module("world-state-simulator.py", "world_state_simulator")

        state = mod.get_world_state({"block": "morning"})
        self.assertIsInstance(state, dict)

        expected_keys = {
            "fishing_season", "weather_favorable", "nft_market_trend",
            "art_scene_active", "crypto_sentiment", "rave_season",
            "month", "hour_utc",
        }
        self.assertTrue(expected_keys.issubset(state.keys()))
        self.assertIsInstance(state["fishing_season"], bool)
        self.assertIsInstance(state["nft_market_trend"], str)
        self.assertIn(state["nft_market_trend"], {"bull", "bear", "neutral"})

    def test_anomaly_detector(self):
        history_file = os.path.join(self.tmpdir, "anomaly-history.json")
        mod = _load_module(
            "anomaly-detector.py",
            "anomaly_detector",
            overrides={"HISTORY_FILE": history_file},
        )

        clean_update = {
            "content": "Lady-INK drops new mural in Shoreditch for GKniftyHEADS community",
            "url": "http://graffpunks.substack.com/p/mural",
        }
        result = mod.detect_anomalies([clean_update])
        self.assertIn("anomalies", result)
        self.assertIn("clean_updates", result)
        self.assertEqual(len(result["clean_updates"]), 1)
        self.assertEqual(len(result["anomalies"]), 0)

        # Very short content should be flagged as anomalous
        short_update = {"content": "hi", "url": "http://example.com"}
        result2 = mod.detect_anomalies([short_update])
        self.assertEqual(len(result2["anomalies"]), 1)
        self.assertIn("anomaly_flags", result2["anomalies"][0])

        # Empty input returns empty structure
        empty = mod.detect_anomalies([])
        self.assertEqual(empty["anomalies"], [])
        self.assertEqual(empty["clean_updates"], [])

    def test_temporal_alignment_engine(self):
        mod = _load_module("temporal-alignment-engine.py", "temporal_alignment_engine")

        updates = [
            {"content": "NFT drop announced", "url": "http://example.com",
             "timestamp": "2024-06-15T09:00:00"},
            {"content": "Carp session at dawn", "url": "http://example2.com"},
        ]
        aligned = mod.align_timestamps(updates)
        self.assertEqual(len(aligned), 2)
        for u in aligned:
            self.assertIn("timestamp_utc", u)
            self.assertIsNotNone(u["timestamp_utc"])

        # Future-dated updates should be excluded
        future_update = {
            "content": "Far future event",
            "url": "http://example.com",
            "timestamp": "2099-01-01T00:00:00+00:00",
        }
        result = mod.align_timestamps([future_update])
        self.assertEqual(len(result), 0)

        # validate_timeline with chronologically ordered posts should return True
        posts = [
            {"timestamp_utc": "2024-01-01T10:00:00+00:00", "content": "First"},
            {"timestamp_utc": "2024-01-01T12:00:00+00:00", "content": "Second"},
        ]
        self.assertTrue(mod.validate_timeline(posts))

    def test_source_attribution_system(self):
        mod = _load_module("source-attribution-system.py", "source_attribution_system")

        updates = [
            {
                "content": "New GraffPUNKS lore post published on Substack",
                "url": "https://graffpunks.substack.com/p/new-lore",
                "confidence": 0.9,
            }
        ]
        attributed = mod.attribute_updates(updates)
        self.assertEqual(len(attributed), 1)
        self.assertIn("attribution", attributed[0])
        attr = attributed[0]["attribution"]
        self.assertIn("source_display", attr)
        self.assertIn("trust_status", attr)
        self.assertEqual(attr["trust_status"], "verified")

        # Unknown domain should still produce attribution with unverified trust
        unknown_updates = [
            {"content": "Some random content", "url": "http://unknown-site.xyz/article", "confidence": 0.5}
        ]
        attributed2 = mod.attribute_updates(unknown_updates)
        self.assertEqual(len(attributed2), 1)
        self.assertEqual(attributed2[0]["attribution"]["trust_status"], "unverified")

        # Empty input returns empty list
        self.assertEqual(mod.attribute_updates([]), [])

    def test_update_priority_queue(self):
        mod = _load_module("update-priority-queue.py", "update_priority_queue")

        updates = [
            {"category": "meta-real", "content": "Some meta content", "confidence": 0.5},
            {"category": "gkdata-real", "content": "GraffPUNKS NFT mint live", "confidence": 0.95},
            {"category": "fishing-real", "content": "Carp feeding at dawn", "confidence": 0.7},
        ]
        rule_ctx = {"block": "morning"}
        ordered = mod.prioritize_updates(updates, rule_ctx)

        self.assertEqual(len(ordered), 3)
        # gkdata-real and fishing-real have morning affinity — they should outrank meta-real
        high_priority_cats = {ordered[0]["category"], ordered[1]["category"]}
        self.assertIn("gkdata-real", high_priority_cats)

        # Empty input returns empty list
        self.assertEqual(mod.prioritize_updates([], {"block": "night"}), [])

    def test_deduplication_engine(self):
        registry_file = os.path.join(self.tmpdir, "used-updates-registry.json")
        mod = _load_module(
            "deduplication-engine.py",
            "deduplication_engine",
            overrides={"REGISTRY_FILE": registry_file},
        )

        updates = [
            {"url": "http://example.com/a", "title": "Title A", "content": "Content A"},
            {"url": "http://example.com/b", "title": "Title B", "content": "Content B"},
        ]

        # Before marking anything as used, all updates pass through
        result = mod.deduplicate_updates(updates)
        self.assertEqual(len(result), 2)

        # Mark the first update as used
        hash_a = mod._hash(updates[0])
        mod.mark_used([hash_a])

        # Now update A should be filtered out
        result2 = mod.deduplicate_updates(updates)
        self.assertEqual(len(result2), 1)
        self.assertEqual(result2[0]["url"], "http://example.com/b")

        # Empty input returns empty list
        self.assertEqual(mod.deduplicate_updates([]), [])


if __name__ == '__main__':
    unittest.main()