[//]: # (excode-config: mode=bash)

This readme shows an example of bash code extraction.
The excode-config is set to bash so all bash-tagged code blocks will be extracted and run. 
The validation is run in Python using Python syntax where all the output printed by the bash test is in a string variable called stdout.
It's nesting in the foo/bar directory also shows how the output tests are generated.

```bash
echo "Hello"
echo "World"
```

[//]: # (excode-validation:
    assert stdout == "Hello\nWorld\n"
)
