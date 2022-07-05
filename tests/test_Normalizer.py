import pytest

from eol.normalization import Normalizer


class TestNormalizer:
    def test_normalize(self, normalizer, non_normalized_data):
        normalized_data = normalizer.normalize(non_normalized_data)
        assert normalized_data == {
            'normalized-key': 12345,
            'another-key': 'foo',
            'normalized-key-1': 'bar'
        }

    @pytest.fixture
    def normalizer(self):
        return DummyNormalizer()

    @pytest.fixture
    def non_normalized_data(self):
        return {
            'non-normalized-key': 12345,
            'another-key': 'foo',
            'un_normalized_key-1': 'bar',
            'key-to-delete': 'buzz'
        }


class DummyNormalizer(Normalizer):
    normalized_keys = {
        'non-normalized-key': 'normalized-key',
        'un_normalized_key-1': 'normalized-key-1'
    }

    delete_keys = ['key-to-delete']
