"""All the tests"""
import random
import string
import unittest
from redis import Redis

from ibloom import IBloom, IBloomException

HOST = '127.0.0.1'
PORT = 6379


def sample_strings(length, count):
    """Return a set of sample strings"""
    return [''.join(
        random.sample(string.ascii_lowercase, length)) for _ in range(count)]


class BaseTest(unittest.TestCase):
    CAPACITY = 10000
    ERROR_RATE = 0.1
    KEY = 'ibloomTesting'

    def setUp(self):
        self.bloom = IBloom(self.KEY, self.CAPACITY, self.ERROR_RATE, HOST, PORT)
        self.redis = Redis(host='127.0.0.1', port=6383)

    def tearDown(self):
        """Remove the bloom filter at the provided test key in all databases"""
        databases = int(self.redis.config_get('databases').get('databases', 0))
        for db in range(databases):
            self.bloom.delete()


class ErrorsTest(BaseTest):
    """Tests about various error conditions"""

    def test_connection_refused(self):
        """In this test I want to make sure that we can catch errors when
        connecting to a redis instance"""
        self.assertRaises(IBloomException, IBloom, 'ibloomTesting', 100, 0.01, port=1234)

    def test_error(self):
        """If we encounter a redis error, we should raise exceptions"""
        self.bloom.delete()
        # If it's the wrong key type, we should see errors. Specifically, this has one
        # of the keys used as a hash instead of a string.
        self.redis.hmset('ibloomTesting.0', {'hello': 5})
        self.assertRaises(IBloomException, self.bloom.add, 'hello')
        self.assertRaises(IBloomException, self.bloom.update, ['a', 'b'])
        self.assertRaises(IBloomException, self.bloom.contains, 'a')
        self.assertRaises(IBloomException, self.bloom.intersection, ['a', 'b'])
        self.redis.delete('ibloomTesting.0')


class FunctionalityTest(BaseTest):
    def test_01_add(self):
        """Make sure we can add, check existing in a basic way"""
        tests = ['hello', 'how', 'are', 'you', 'today']
        for test in tests:
            self.bloom.add(test)
        for test in tests:
            self.assertTrue(test in self.bloom)

    def test_02_update(self):
        """Make sure we can use the extend method to the same effect"""
        tests = ['hello', 'how', 'are', 'you', 'today']
        self.bloom.update(tests)
        for test in tests:
            self.assertTrue(test in self.bloom)

    def test_03_intersection(self):
        """Make sure contains returns a list when given a list"""
        tests = ['hello', 'how', 'are', 'you', 'today']
        self.bloom.update(tests)
        self.assertEqual(tests, self.bloom.intersection(tests))

    def test_04_two_instances(self):
        """Make sure two bloom filters pointing to the same key work"""
        bloom = IBloom('ibloomTesting', 10000, 0.1, HOST, PORT)
        tests = ['hello', 'how', 'are', 'you', 'today']

        # Add them through the first instance
        self.bloom.update(tests)
        self.assertEqual(tests, self.bloom.intersection(tests))

        # Make sure they're accessible through the second instance
        self.assertEqual(tests, bloom.intersection(tests))

    def test_05_delete(self):
        """Make sure that when we delete the bloom filter, we really do"""
        samples = sample_strings(20, 5000)
        self.bloom.update(samples)
        self.bloom.delete()
        self.assertEqual(len(self.bloom.intersection(samples)), 0, 'Failed to actually delete filter')


class DbTest(BaseTest):
    """Make sure we can select a database"""

    def test_select_db(self):
        """Can instantiate a bloom filter in a separate db"""
        bloom = IBloom(self.KEY, self.CAPACITY, self.ERROR_RATE, db=1, host=HOST, port=PORT)

        # After adding key to our db=0 bloom filter, shouldn't see it in our db=0 bloom
        samples = sample_strings(20, 100)
        self.bloom.update(samples)
        self.assertEqual(len(bloom.intersection(samples)), 0)


class AllocationTest(BaseTest):
    """Tests about large allocations"""
    CAPACITY = 200000000
    ERROR_RATE = 0.00001

    def test_size_allocation(self):
        """Make sure we can allocate a bloom filter that would take more than 512MB (the string size limit in Redis)"""
        included = sample_strings(20, 5000)
        excluded = sample_strings(20, 5000)

        # Add only the included strings
        self.bloom.update(included)
        self.assertEqual(len(included), len(self.bloom.intersection(included)))

        false_positives = self.bloom.intersection(excluded)
        false_rate = float(len(false_positives)) / len(excluded)
        self.assertTrue(false_rate <= 0.00001, 'False positive error rate exceeded!')

        # We also need to know that we can access all the keys we need
        self.assertEqual(self.bloom.keys(), ['ibloomTesting.0', 'ibloomTesting.1'])


class Accuracytest(BaseTest):
    """Make sure we meet our accuracy expectations for the bloom filter"""

    def test_random(self):
        """Insert some random strings, make sure we don't see another set of
        random strings as in the bloom filter"""
        included = sample_strings(20, 5000)
        excluded = sample_strings(20, 5000)

        # Add only the included strings
        self.bloom.update(included)
        self.assertTrue(len(included) == len(self.bloom.intersection(included)))

        false_positives = self.bloom.intersection(excluded)
        false_rate = float(len(false_positives)) / len(excluded)
        self.assertTrue(false_rate <= 0.1, 'False positive error rate exceeded!')


if __name__ == '__main__':
    unittest.main()
