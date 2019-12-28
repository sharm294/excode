[//]: # (excode-config: mode=python)

This readme shows an example of filtered code extraction and wildcard imports.
The excode-config is set to python so all python-tagged code blocks will be extracted and run.
In this case, that means the c-tagged block will be ignored.  
The validation uses the optional index specification to say that this validation belongs to the zero-th (first) block of testing code.
If no index is specified, the validation blocks are attached to the code blocks in the same order that they appear.
It's nesting in the foo/ directory also shows how the output tests are generated.

```c
int a = 4 + 5 + 6;
```

```python
from os import * # dummy asterisk style import
b = 1 + 2 + 3
```

[//]: # (excode-validation: 0
    assert b == 6
)
