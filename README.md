## ibloom


this is a fork of [pyreBloom-ng](https://github.com/leovp/pyreBloom-ng), pyreBloom-ng is a python library which implements a Redis-backed Bloom filter.

pyreBloom-ng is really powerful. but it's setup.py and tests and bench/benchmark.py are all outdated, the repo's last commit is 4 years ago.

based on pyreBloom-ng and added supported for python3's str, avoid of annoying *`b'some_key'`*

## Installation

### pre-requirement
`ibloom` requires `hiredis` library, `Cython` and `a C compiler`


> hiredis

```sh
# Mac
brew install hiredis

# ubuntu
apt-get install libhiredis-dev

# From source:
git clone https://github.com/redis/hiredis
cd hiredis && make && sudo make install
```

> Cython

```sh
pip install Cython
```

## Startup

### init an instance

```python
from ibloom import IBloom
ib = IBloom('ibloomI', 1000, 0.01, '127.0.0.1', 6383)
```
or
```python
from ibloom import IBloom
ib_n = IBloom(key='ibloomN', capacity=1000, error=0.01, host='127.0.0.1', port=6383)
```

### check basic info

```python
# You can find out how many bits this will theoretically consume
>>> ib.bits
9585
# And how many hashes are needed to satisfy the false positive rate
>>> ib.hashes
7
# find all available bloom filter keys
>>> ib.keys()
['ibloomI.0']
```

### add data

#### add all supplied

```python
# Add one value at a time (slow)
>>> ib.add('first')
True
# Or use batch operations (faster).
>>> ib.update([f'{x}' for x in range(5)])
5
# Alternative: ib += data, but this will return nothing
>>> ib += [f'{x + 5}' for x in range(5)]
```

#### only add if not exist

```python
# will first get the difference, and then update them to redis, and return them
>>> ib.update_difference(['5', '6', '7', '8', '9', '10'])
['10']
```

### check if key exists

#### find one

```python
# Test one value at a time (slow).
# . in ...
>>> 'first' in ib
True
# ...contains(.)
>>> ib.contains('first')
True
```

#### find multiple

```python
# Use batch operations (faster).
# Note: ibloom.intersection() returns a list of values
# which are found in a Bloom filter. It makes sense when
# you consider it a set-like operation.
>>> ib.intersection(['3', '4', '5', '6'])
['3', '4', '5', '6']
# Alternative: ib & [b'3', b'4', b'5', b'6']
>>> ib & ['3', '4', '5', '6', '9', '10']
['3', '4', '5', '6', '9']
```

#### find non exist

```python
>>> ib.difference(['5', '6', '7', '8', '9', '10'])
['10']
# not recommended, maybe update in the future
# Alternative: ib ^ ['5', '6', '7', '8', '9', '10']
>>> ib ^ ['5', '6', '7', '8', '9', '10']
['10']
```

### delete the bloom key

```python
# delete self
ib.delete()
```
