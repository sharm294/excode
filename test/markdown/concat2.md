[//]: # (excode-config: mode=python)

This readme shows an example of code concatenation.
The excode-config is set to python so all python-tagged code blocks will be extracted and run.
The third code block uses the attach keyword to concatenate this code block to a prior one.
An integer 0 is being used to attach it to the 0-th code block (the first one).
This results in a two tests test being generated with the first test containing the first and third code blocks and the second test containing the second code block.

```python
add = 1 + 2 + 3
print(add)
```

```python
add = 4 + 5
print(add)
```

```python excode: attach=0
add = 6 + 7
print(add)
```
