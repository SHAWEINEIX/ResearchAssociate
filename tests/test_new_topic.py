#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""new_topic 的测试：建目录、模板替换、台账更新、重复保护。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import new_topic  # noqa: E402
import research_common as rc  # noqa: E402


class NewTopicTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_topics = rc.TOPICS_DIR
        self.old_index = rc.INDEX_PATH
        self.old_update = rc.update_index
        rc.TOPICS_DIR = self.root / "topics"
        rc.TOPICS_DIR.mkdir()
        rc.INDEX_PATH = rc.TOPICS_DIR / "index.md"
        rc.INDEX_PATH.write_text(
            "# 台账\n\n<!-- AUTO:TOPICS:BEGIN -->\n<!-- AUTO:TOPICS:END -->\n",
            encoding="utf-8",
        )

    def tearDown(self):
        rc.TOPICS_DIR = self.old_topics
        rc.INDEX_PATH = self.old_index
        self.tmp.cleanup()

    def test_create(self):
        code = new_topic.main(["测试题目", "--slug", "test-topic", "--date", "2026-10-19", "--depth", "L1"])
        self.assertEqual(code, 0)
        topic = rc.TOPICS_DIR / "2026-10-19-test-topic"
        for name in ("brief.md", "plan.md", "evidence.md", "log.md"):
            self.assertTrue((topic / name).exists(), name)
        brief = (topic / "brief.md").read_text(encoding="utf-8")
        self.assertIn("测试题目", brief)
        self.assertIn("2026-10-19", brief)
        self.assertIn("L1", brief)
        self.assertNotIn("{{", brief)
        index = rc.INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("2026-10-19-test-topic", index)

    def test_duplicate(self):
        new_topic.main(["测试题目", "--slug", "test-topic", "--date", "2026-10-19"])
        code = new_topic.main(["测试题目", "--slug", "test-topic", "--date", "2026-10-19"])
        self.assertEqual(code, 1)

    def test_similar(self):
        new_topic.main(["房地产 AI 培训市场", "--slug", "ai-training", "--date", "2026-10-19"])
        found = new_topic.similar_topics("房地产 AI 培训市场分析")
        self.assertTrue(found)
        self.assertEqual(found[0][2], "2026-10-19-ai-training")

    def test_slugify(self):
        self.assertEqual(new_topic.slugify("AI Training Market 2026"), "ai-training-market-2026")
        self.assertTrue(new_topic.slugify("房地产").startswith("topic-"))


if __name__ == "__main__":
    unittest.main()
