# FASTA Annotation
Extending the FASTA File format to allow for extendable annotations to be added in an efficient computer-parsable form. 


# Usage Guide

## Importing the parser
The parser class uses the Python3 standard library so any version of Python3 should already have the packages you need. More specifically we use the `defauldict` package from `collections` and the `json` package. 

Adding the file `fastannotation.py` to your working directory importing the `fastannotation` package will expose the `Parser` class to you for use. This can be done in a few different ways:

`import fastannotation` will require you to prepend the `fastannotation` package descriptor to your Parser initialization statements as follows: 


```python
import fastannotation
parser = fastannotation.Parser(...)
```


`from fastannotation import *` is the recommended import style as it will import all classes and functions within the `fastannotation.py` class eliminating the need to prepend `fastannotation` to your `Parser` instantiations


```python
from fastannotation import *
parser = Parser(...)
```

## FASTA Layout

### Normal FASTA

```
> primary_key1 value1 value2 value3
ACGTACGTACGTACGT
> primary_key2 value4 value5 value6
GCATGCATGCATGCAT
```
In a normal FASTA file we see alternating header and sequence lines with header lines indicated with leading `>` character. Headers will define some unique key that allows you to uniquely identify the sequence that directly follows it. In the example above it is the `primary_key*` value in each header that uniquely defines each sequence. 

### Our FASTA extension

```
> primary_key1 value1 value2 value3 {"key1":"value1", ...}
ACGTACGTACGTACGT
> primary_key2 value4 value5 value6 {"key2":"value2", ...}
GCATGCATGCATGCAT
```

Our key addition to the existing FASTA file format is allowing for the addition of a JSON object at the end exisiting headers. This extension allows for free editing of the FASTA file through the addition of `key:value` pairs to the JSON object at the end of each header. 

Internally we represent this FASTA file as a python dictionary with the `primary_key*` value as the `key` and the `header` and `sequence` data as the value. It is of paramount importance that the `primary_key*` be well defined and unique for each header, and if they are not well-defined there will be key clashes in the internal representation leading to an inaccurate load of the FASTA file. 


## Class Layout
The parser is entirely encapsulated within the `Parser` object which takes a number of parameters used to load the specified FASTA files. 

Parameters:

* `fasta`:

    * `type`: `str`

    * `description`: The absolute filepath for the input fasta file

    * `Required`: Yes

* `keyIndex`:

    * `type`: `int`
    
    * `description`: Define the index of the primary key in the header.

    * `Required`: No. Defaults to index 0 (first value found right after the `>` in each header) but should be included if `primary_key*` is found somewhere else in the header. 

* `delimiter`:

    * `type`: `str`

    * `description`: Define the delimiter you use in the header. Defaults to "|" but can be any string. 

    * `Required`: No. Defaults to `|` but should be included if delimiter is not `|`


## Internal representation
Internally we represent our FASTA files as a python dictionary. We allow for header files with any number of delimited values, so long as at least one of those values is the `primary_key*` that can be used to uniquely identify the sequence. 

Any remaining headers, not including the `JSON` object at the end of the header, will be added into a list which is inserted into the internal dictionary using a reserved key called `delimited`. 

Given the following file:

```
> primary_key1 value1 value2 value3
ACGTACGTACGTACGT
> primary_key2 value4 value5 value6
GCATGCATGCATGCAT
```

The internal dicitonary representation would look like: 

```json
{
    "primary_key1": {
        "delimited": ["value1", "value2", "value3"], 
        "seq": "ACGTACGTACGTACGT"
    },
    "primary_key2": {
        "delimited": ["value4", "value5", "value6"],
        "seq": "GCATGCATGCATGCAT"
    }
}
```

Given a FASTA file with a JSON annotation object like the following:

```
> primary_key1 value1 value2 value3 {"key1":"value1"}
ACGTACGTACGTACGT
> primary_key2 value4 value5 value6 {"key2":"value2"}
GCATGCATGCATGCAT
```

The internal dictionary representation would look like:

```json
{
    "primary_key1": {
        "delimited": ["value1", "value2", "value3"], 
        "seq": "ACGTACGTACGTACGT", 
        "key1": "value1"
    },
    "primary_key2": {
        "delimited": ["value4", "value5", "value6"],
        "seq": "GCATGCATGCATGCAT", 
        "key2": "value2"
    }
}
```

You can see above that the JSON object at the end of the header lines was integrated into the internal python dictionary alongside the `delimited` and `seq` keys. 

## Examples of FASTA files and appropriate loading syntax and results

### Ex 1

Assume the following FASTA file has filename `fasta.fa`:

```
> primary_key1 value1 value2 value3
ACGTACGTACGTACGT
> primary_key2 value4 value5 value6
GCATGCATGCATGCAT
```

The appropriate load of this file using the `fastannotation` package is:

```python
from fastannotation import *
sequences = Parser('fasta.fa', delimiter=" ")
```

Note that since the `primary_key*` is the first element after the header we don't need to pass the `keyIndex` parameter to the parser.

The code above will result in the internal dictionary structure:

```json
{
    "primary_key1": {
        "delimited": ["value1", "value2", "value3"], 
        "seq": "ACGTACGTACGTACGT"
    },
    "primary_key2": {
        "delimited": ["value4", "value5", "value6"],
        "seq": "GCATGCATGCATGCAT"
    }
}
```

### Ex 2

Assume the following FASTA file has filename `fasta.fa`

```
> value1;primary_key1;value2;value3;{"key1":"value1"}
ACGTACGTACGTACGT
> value4;primary_key2;value5;value6;{"key2":"value2"}
GCATGCATGCATGCAT
```

```python
from fastannotation import *
sequences = Parser("fasta.fa", keyIndex=1, delimiter=";")
```

The code above will result in the internal dictionary structure:

```json
    "primary_key1": {
        "delimited": ["value1", "value2", "value3"], 
        "seq": "ACGTACGTACGTACGT", 
        "key1": "value1"
    },
    "primary_key2": {
        "delimited": ["value4", "value5", "value6"],
        "seq": "GCATGCATGCATGCAT", 
        "key2": "value2"
    }
```

## API Methods

Defining the basic API methods exposed by the FastAnnotation parser

Assume the following FASTA file has filename `fasta.fa`

```
> value1;primary_key1;value2;value3;{"key1":"value1"}
ACGTACGTACGTACGT
> value4;primary_key2;value5;value6;{"key2":"value2"}
GCATGCATGCATGCAT
```

We will use this file for all our examples. 

### `keys()`

Returns a list of keys that currently exist in the internal dictionary.

The snippet below will print out the list of keys that are currently in the dictionary.
```python
from fastannotation import *
sequences = Parser("fasta.fa", keyIndex=1, delimiter=";")
listOfKeys = sequences.keys()
print(listOfKeys)
```

Output:

```
["primary_key_1", "primary_key_2"]
```
### `write(outfile)`

Write out the current Parser state to the provided output file. If edits have been made to the parser output they will be reflected in the written file.

Parameters:

* `outfile`:

    * Type: `str`

    * Description: Absolute path to the output file. If the file exists it will be overwritten

```python
from fastannotation import *
sequences = Parser("fasta.fa", keyIndex=1, delimiter=";")
outfile = "copy_of_fasta.fa"
sequences.write(outfile)
```

Loads the FASTA file and writes out a copy of it to the file `copy_of_fasta.fa`

### `keyDict()`

Return a list of all currently used annotation keys with type information associated with the key.
This is an expensive operation and should only be used when adding new annotation information to a file.

```python
from fastannotation import *
sequences = Parser("fasta.fa", keyIndex=1, delimiter=";")
keyDict = sequences.keyDict()
print(keyDict)
```

Output:

```json
{"delimited": "list", "seq": "str", "key1": "str", "key2": "str"}
```
### `findInstances(key, limit=-1)`

Returns a list of all values corresponding to a certain key. This is used to find examples of a given key's values currently in the internal dictionary. 
This can be an expensive operation. In the worst case this will scan through the entire internal dictionary and de-serialize all un-serialized JSON objects found along the way. 

Parameters:

* `key`

    * Type: `str`

    * Description: key you are looking for examples of

    * Required: yes

* `limit`

    * Type: `int`

    * Description: The upper limit to the number of examples you want. 

    * Required: no. Defaults to return all examples foudn in the internal dictionary.  

```python
from fastannotation import *
sequences = Parser("fasta.fa", keyIndex=1, delimiter=";")
# With limit
examples_1 = sequences.findInstances("delimited", limit=1) 
# Without limit
examples_2 = sequences.findInstances("seq")                
print("ex1: ", examples_1)
print("ex2: ", examples_2)
```

Output: 

```python
ex1: [["value1", "value2", "value3"]]
ex2: ["ACGTACGTACGTACGT", "GCATGCATGCATGCAT"]
```
## API Basic Usage

After loading your desired FASTA file there are a few key actions we will define that allow you to interact with the data. 
For the following examples, assume that the Parser object has been instantiated as follows:

Assume the following FASTA file has filename `fasta.fa`

```
> value1;primary_key1;value2;value3;{"key1":"value1"}
ACGTACGTACGTACGT
> value4;primary_key2;value5;value6;{"key2":"value2"}
GCATGCATGCATGCAT
```

```python
from fastannotation import *
sequences = Parser("fasta.fa", keyIndex=1, delimiter=";")
```

### Accessing annotations for a given key

The `Parser` object can be indexed just like any other python dictionary. If I wanted to see the `header` and `seq` information for the key `primary_key_1` I would run the following command: 

```python
pk1Annotations = sequences["primary_key_1"]
print(pk1Annotations["seq"])
print(pk1Annotations["key1"])
```

Output:

```json
"ACGTACGTACGTACGT"
"value1"
```

### Updating an existing annotation

The power of the FastAnnotation library comes from the ability to freely update the annotation values in the Parser object. Let's assume we want to change the `"key1"` value in `"primary_key_1"` from `"value1"` to `"value10"`.

```python
sequences["primary_key_1"]["key1"] = "value10"
print(sequences["primary_key_1"]["key1"])
sequences.write("outfile.fa")
```

This example shows how to update an existing key value in the Parser. Writing out the file like above will write out the updated dictionary so the change you made is now reflected in the actual FASTA file. 

```python
"value10"
```

### Adding new Annotations

While this can be done in essentially the same way as the update we did above, I will define a recommended methodology you should use to prevent key clashes and other potentially disasterous file errors. 

Lets assume we want to add a label called `"lab"` to the `"primary_key_1"` header that defines the lab in which the sequence data was actually sequenced in. 

We would do this in a number of steps outlined below:

```python
# Get all the existing keys
keyDict = sequences.keyDict()
# Check to see if the key you want to add already exists
assert("lab" not in keyDict)
```

It is important to note that the `.keyDict()` method is expensive as it iterates through the entire internal dictionary of data and de-serializes JSON objects that are still in string form while also doing a scan through each entry to get all of the existing keys. We imagine that this method will only be used when exploring new annotation names and should not exist in any regularly running code.

We can now add the key and the value as we did in the update methodolgy we described above. 

```python
sequences["primary_key_1"]["lab"] = "University of North Carolina at Chapel Hill"
sequences.write("outfile.fa")
```

This updates the `"primary_key_1"` with the `"lab"` annotation and then writes the updated dictionary out to a new FASTA file. 

