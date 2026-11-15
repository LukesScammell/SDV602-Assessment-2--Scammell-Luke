import csv
import tempfile
import unittest
from pathlib import Path

from data_visualiser import DataVisualiser


class TestDataVisualiser(unittest.TestCase):
    def setUp(self):
        self.visualiser = DataVisualiser()

    def test_initial_data_is_empty(self):
        """A new visualiser should start without records."""
        self.assertEqual(self.visualiser.get_data(), [])

    def test_load_data(self):
        """Records should be loaded into the visualiser."""
        records = [
            {"Period": "2025", "Count": "100"},
            {"Period": "2026", "Count": "120"},
        ]

        result = self.visualiser.load_data(records)

        self.assertTrue(result)
        self.assertEqual(len(self.visualiser.get_data()), 2)

    def test_load_empty_data(self):
        """Empty datasets should be rejected."""
        result = self.visualiser.load_data([])

        self.assertFalse(result)
        self.assertEqual(self.visualiser.get_data(), [])

    def create_test_csv(self, directory, filename, columns, rows):
        """Create a temporary CSV file for testing."""
        path = Path(directory) / filename

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        return str(path)

    def test_load_csv(self):
        """Loading a CSV should populate the dataset."""
        with tempfile.TemporaryDirectory() as directory:
            path = self.create_test_csv(
                directory,
                "population.csv",
                ["Period", "Count"],
                [
                    {"Period": "2025", "Count": "100"},
                    {"Period": "2026", "Count": "120"},
                ],
            )

            result = self.visualiser.load_csv(path)

            self.assertTrue(result)
            self.assertEqual(len(self.visualiser.get_data()), 2)

    def test_append_csv(self):
        """Appending a compatible CSV should add records."""
        with tempfile.TemporaryDirectory() as directory:
            first_path = self.create_test_csv(
                directory,
                "first.csv",
                ["Period", "Count"],
                [{"Period": "2025", "Count": "100"}],
            )
            second_path = self.create_test_csv(
                directory,
                "second.csv",
                ["Period", "Count"],
                [{"Period": "2026", "Count": "120"}],
            )

            self.visualiser.load_csv(first_path)
            result = self.visualiser.append_csv(second_path)

            self.assertTrue(result)
            self.assertEqual(len(self.visualiser.get_data()), 2)

    def test_append_mismatched_columns(self):
        """Incompatible CSV columns should be rejected."""
        with tempfile.TemporaryDirectory() as directory:
            first_path = self.create_test_csv(
                directory,
                "first.csv",
                ["Period", "Count"],
                [{"Period": "2025", "Count": "100"}],
            )
            second_path = self.create_test_csv(
                directory,
                "second.csv",
                ["Year", "Population"],
                [{"Year": "2026", "Population": "120"}],
            )

            self.visualiser.load_csv(first_path)
            result = self.visualiser.append_csv(second_path)

            self.assertFalse(result)
            self.assertEqual(len(self.visualiser.get_data()), 1)

    def test_nonexistent_csv(self):
        """Missing CSV files should not load successfully."""
        with tempfile.TemporaryDirectory() as directory:
            missing_path = str(Path(directory) / "nonexistent.csv")

            result = self.visualiser.load_csv(missing_path)

            self.assertFalse(result)

    def test_switch_dataset(self):
        """Loading another CSV should replace the current dataset."""
        with tempfile.TemporaryDirectory() as directory:
            first_path = self.create_test_csv(
                directory,
                "first.csv",
                ["Period", "Count"],
                [{"Period": "2025", "Count": "100"}],
            )

            second_path = self.create_test_csv(
                directory,
                "second.csv",
                ["Year", "Population"],
                [
                    {"Year": "2026", "Population": "120"},
                    {"Year": "2027", "Population": "140"},
                ],
            )

            self.visualiser.load_csv(first_path)
            result = self.visualiser.load_csv(second_path)

            self.assertTrue(result)
            self.assertEqual(len(self.visualiser.get_data()), 2)
            self.assertIn("Year", self.visualiser.get_data()[0])
            self.assertNotIn("Period", self.visualiser.get_data()[0])


if __name__ == "__main__":
    unittest.main()
