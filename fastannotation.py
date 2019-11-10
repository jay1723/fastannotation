import json
from collections import defaultdict

class Parser:
    """
    A basic wrapper for a FASTA file parser that allows for extensible JSON headers in addition to existing delimited headers.
    We define the basic operations for a FASTA file including reading and writing while also providing JSON header writing functionality.
    """
    def __init__(self, fasta, keyIndex=0, delimiter="|"):
        """
        Input:
            fasta: <str> - The absolute filepath for the input fasta file
            keyIndex: <int> - Key should always be in the delimited section. If there is more than one item in the delimited section this defines the index of the primary key in the delimited section
            delimiter: <str> - Define the delimiter you use for the delimited section. Defaults to "|" but can be any string

        Output:
            Parser object instance with parsed fasta file stored in internal dictionary
        """
        # Initialize instance variables
        self.data = defaultdict(dict)
        self.keyIndex = keyIndex
        self.delimiter = delimiter
        self.fasta = fasta

        with open(fasta, "r") as fp:
            hdr = fp.readline().strip()[1:] # Removes the '>' char
            seq = fp.readline().strip()
            while hdr and seq:
                delimited = [] # Store the remaining delimited section
                hdr = hdr.split(delimiter)
                key = hdr.pop(self.keyIndex)
                self.data[key]["seq"] = seq

                # If there is JSON in the hdr it must be the last element
                if len(hdr) > 0 and hdr[-1][0] == "{":
                    self.data[key]["json"] = hdr.pop()

                # Remainder of the hdr goes into the delmited keyword section
                if len(hdr) > 0:
                    self.data[key]["delimited"] = hdr

                hdr = fp.readline().strip()[1:]
                seq = fp.readline().strip()

    def __getitem__(self, key):
        """
        Overloading the [] operator for the Parser class
        This method resolves headers that we lazily evaluated on reading so that the full attributes are materialized if they exist.

        Input:
            key: <Object> - The key tied to the value you want to read.
        """
        # If there is an unloaded JSON section, load it and merge the dictionaries
        if key in self.data:
            if "json" in self.data[key]:
                jval = json.loads(self.data[key]["json"])
                del self.data[key]["json"]
                self.data[key].update(jval)
            return self.data[key]
        else:
            return None


    # Sets a new dictionary value. Assumes that the value is a dictionary
    def __setitem__(self, key, value):
        """
        Overloading the "[] =" operator.

        Input:
            key: <Object> - The key tied to the value you want to insert.
            value: <Object> - the value you with to insert
        """
        # Load/resolve any json before adding new keys
        self[key] # Should call __getitem__
        self.data[key] = value

    def __len__(self):
        """
        Overloading the len() operator to make it return the length of the dictionary
        """
        return len(self.data)

    def write(self, outfile):
        """
        Write out the current Parser state to the provided output file. If edits have been made to the parser output they will be reflected in the written file.

        Input:
            outfile: <str> - Absolute path to the output file. If the file exists it will be overwritten

        Output:
            output file is written.
        """
        with open(outfile, 'w+') as fp:
            for key in self.data:
                self[key] # Materialize the JSON objects
                writestr = ">" + key
                # Remove the sequence from the dictionary
                seq = self.data[key]["seq"] + "\n"
                del self.data[key]["seq"]
                if "delimited" in self.data[key]:
                    self.data[key]["delimited"][self.keyIndex:self.keyIndex] = [key]
                    writestr += self.delimiter.join([str(v) for v in self.data[key]["delimited"]])
                    del self.data[key]["delimited"]

                writestr += self.delimiter
                if len(self.data[key]) > 0:
                    writestr += json.dumps(self.data[key], separators=(',',':')) + "\n"
                fp.write(writestr)
                fp.write(seq)
