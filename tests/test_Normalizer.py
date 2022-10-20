import pytest

from eol.normalization import Normalizer


class TestNormalizer:
    def test_normalize(self, normalizer, non_normalized_data):
        normalized_data = normalizer.normalize(non_normalized_data)
        assert normalized_data == {
            "normalized-key": 12345,
            "another-key": "foo",
            "normalized-key-1": "bar",
            "already-normalized-key": "foobar",
        }

    def test_multiple_keys_mapping_same_value(self, normalizer, non_normalized_data):
        normalizer.normalized_keys["duplicate_mapping"] = "normalized-key"
        non_normalized_data["duplicate_mapping"] = None

        normalized_data = normalizer.normalize(non_normalized_data)
        assert normalized_data == {
            "normalized-key": 12345,
            "another-key": "foo",
            "normalized-key-1": "bar",
            "already-normalized-key": "foobar",
        }

    def test_raises_exception_when_multimapping_leads_to_value_collision(
        self, normalizer, non_normalized_data
    ):
        """When two keys map the same normalized value and both keys hold
        valid data, an exception should be raised."""
        normalizer.normalized_keys["duplicate_mapping"] = "normalized-key"
        non_normalized_data["duplicate_mapping"] = 6789

        with pytest.raises(ValueError):
            normalizer.normalize(non_normalized_data)

    @pytest.fixture
    def normalizer(self):
        return DummyNormalizer()

    @pytest.fixture
    def non_normalized_data(self):
        return {
            "non-normalized-key": 12345,
            "another-key": "foo",
            "un_normalized_key-1": "bar",
            "key-to-delete": "buzz",
            "already-normalized-key": "foobar",
        }


class DummyNormalizer(Normalizer):
    normalized_keys = {
        "non-normalized-key": "normalized-key",
        "un_normalized_key-1": "normalized-key-1",
        "already-normalized-key": "already-normalized-key",
    }

    delete_keys = ["key-to-delete"]
