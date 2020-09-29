import time
import redis
import random
import string
import unittest
from ibloom import IBloom

count = 10000
capacity = count * 2
error = 0.1

HOST = '127.0.0.1'
PORT = 6379

print('Generating %i random test words' % (count * 2))
start = -time.time()
included = [''.join(random.sample(string.ascii_lowercase, 20)) for i in range(count)]
outcluded = [''.join(random.sample(string.ascii_lowercase, 20)) for i in range(count)]
start += time.time()
print('Generated random test words in %fs' % start)

p = IBloom('ibloomTesting', capacity, error, HOST, PORT)
p.delete()

print('Filter using %i hash functions and %i bits' % (p.hashes, p.bits))

start = -time.time()
p.update(included)
start += time.time()
print('Batch insert : %fs (%f words / second)' % (start, (count / start)))

p.delete()
start = -time.time()
r = [p.add(word) for word in included]
start += time.time()
print('Serial insert: %fs (%f words / second)' % (start, (count / start)))

start = -time.time()
r = p.intersection(included)
start += time.time()
print('Batch test   : %fs (%f words / second)' % (start, count / start))

start = -time.time()
r = [(word in p) for word in included]
start += time.time()
print('Serial test  : %fs (%f words / second)' % (start, count / start))

falsePositives = p.intersection(outcluded)
falseRate = float(len(falsePositives)) / len(outcluded)
print('False positive rate: %f (%f expected)' % (falseRate, error))

# Now, let's compare this to adding items to a set in redis
p.delete()
start = -time.time()
r = redis.Redis(host=HOST, port=PORT)
o = r.sadd('ibloomTesting', *included)
start += time.time()
print('Redis set add  : %fs (%f words / second)' % (start, count / start))

start = -time.time()
with r.pipeline() as pipe:
    o = [pipe.sismember('ibloomTesting', word) for word in included]
    results = pipe.execute()
start += time.time()
if sum(int(i) for i in results) != len(included):
    print('REDIS PIPE FAILED!')
print('Redis pipe chk : %fs (%f words / second)' % (start, count / start))

p.delete()
start = -time.time()
with r.pipeline() as pipe:
    o = [pipe.sadd('ibloomTesting', word) for word in included]
    results = pipe.execute()
start += time.time()
print('Redis pipe sadd: %fs (%f words / second)' % (start, count / start))

start = -time.time()
with r.pipeline() as pipe:
    o = [pipe.sismember('ibloomTesting', word) for word in included]
    results = pipe.execute()
start += time.time()
if sum(int(i) for i in results) != len(included):
    print('REDIS PIPE FAILED!')
print('Redis pipe chk : %fs (%f words / second)' % (start, count / start))

p.delete()
