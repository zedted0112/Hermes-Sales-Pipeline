import unittest
from pathlib import Path
from custom.append_note import append_note

class TestCustomTools(unittest.TestCase):
    def test_append_note(self):
        # Path to the notes file
        notes_file = Path(__file__).resolve().parents[1] / "data" / "notes.log"

        # Make sure the file doesn't exist before we start
        if notes_file.exists():
            notes_file.unlink()

        # Call the tool
        result = append_note("This is a test note.")

        # Check that the tool returned a successful result
        self.assertTrue(result.ok)

        # Check that the file was created
        self.assertTrue(notes_file.exists())

        # Check that the note was written to the file
        with open(notes_file, "r") as f:
            content = f.read()
            self.assertIn("This is a test note.", content)

        # Clean up the file
        notes_file.unlink()

if __name__ == '__main__':
    unittest.main()
