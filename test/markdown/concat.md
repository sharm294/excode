[//]: # (excode-config: mode=python)

This readme shows an example of code concatenation.
The excode-config is set to python so all python-tagged code blocks will be extracted and run.
The second code block uses the attach keyword to concatenate this code block to a prior one.
The 'prev' value indicates to attach it to the previous code block.
An integer i can also be used to attach it to the i-th code block (see concat2.md).
This results in a single test being generated containing both code blocks.

```python
add = 1 + 2 + 3
print(add)
```

```python excode: attach=prev
add = 4 + 5
print(add)
```
