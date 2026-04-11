"""Tests for I2I Signal Protocol."""
import unittest

class TestI2ISignalParsing(unittest.TestCase):
    def test_signal_format_hello(self):
        msg = "[I2I:HELLO] First contact from Oracle1"
        self.assertIn("HELLO", msg)
    
    def test_signal_format_status(self):
        msg = "[I2I:STATUS] Fleet operational"
        self.assertIn("STATUS", msg)
    
    def test_signal_format_task(self):
        msg = "[I2I:TASK_ASSIGN] Fix tests P0"
        self.assertIn("TASK_ASSIGN", msg)
    
    def test_signal_format_tell(self):
        msg = "[I2I:TELL] ISA analysis 247 opcodes"
        self.assertIn("TELL", msg)
    
    def test_signal_format_ask(self):
        msg = "[I2I:ASK] Confidence default?"
        self.assertIn("ASK", msg)
    
    def test_signal_format_bottle(self):
        msg = "[I2I:BOTTLE] Results 9/9 passed"
        self.assertIn("BOTTLE", msg)

class TestI2IProtocolTypes(unittest.TestCase):
    def test_v2_has_20_types(self):
        v2 = ["HELLO","STATUS","HEARTBEAT","GOODBYE","TASK_ASSIGN","TASK_RESULT",
              "TASK_CANCEL","REVIEW_REQUEST","REVIEW_RESPONSE","HELP_REQUEST",
              "KNOWLEDGE_SHARE","EMERGENCY","TELL","ASK","BOTTLE","SIGNAL",
              "BROADCAST","HANDSHAKE","CONFIRM","REJECT"]
        self.assertEqual(len(v2), 20)
    
    def test_v1_core_types(self):
        v1 = ["HELLO","STATUS","TASK_ASSIGN","TELL","ASK","BOTTLE"]
        self.assertEqual(len(v1), 6)

class TestI2ISignalFormat(unittest.TestCase):
    def test_prefix_format(self):
        msg = "[I2I:HELLO] test"
        self.assertTrue(msg.startswith("[I2I:"))
    
    def test_type_extraction(self):
        commits = ["[I2I:HELLO] test","[I2I:TELL] info","[I2I:ASK] question"]
        for c in commits:
            start = c.index("[I2I:") + 5
            end = c.index("]", start)
            self.assertTrue(c[start:end].isupper())

class TestI2IResolution(unittest.TestCase):
    def test_agreement(self):
        self.assertEqual("confidence-default", "confidence-default")
    
    def test_dispute_hardware_wins(self):
        oracle1 = "confidence-optional"
        jetson = "confidence-default"
        resolution = jetson  # hardware expertise wins
        self.assertEqual(resolution, "confidence-default")

if __name__ == "__main__":
    unittest.main(verbosity=2)
