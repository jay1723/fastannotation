import json
from collections import defaultdict

class Parser:
    def __init__(self, fasta, keyIndex=0, delimiter="|"):
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
        # Load/resolve any json before adding new keys
        self[key] # Should call __getitem__
        self.data[key] = value

    # When you want to add a specific key:value pair to an exisiting dictionary in the data object
    def addKeyValue(self, key, keydesc, value):
        # Load/resolve any json before adding new keys
        self[key] # Should call __getitem__
        self.data[key][keydesc] = value

    def __len__(self):
        return len(self.data)

    def write(self, outfile):
        with open(outfile, 'w+') as fp:
            for key in self.data:
                self[key] # Materialize the JSON objects
                writestr = ">"
                # Remove the sequence from the dictionary
                seq = self.data[key]["seq"] + "\n"
                del self.data[key]["seq"]
                if "delimited" in self.data[key]:
                    self.data[key]["delimited"][self.keyIndex:self.keyIndex] = [key]
                    writestr += self.delimiter.join([str(v) for v in self.data[key]["delimited"]])
                    del self.data[key]["delimited"]

                writestr += self.delimiter
                if len(self.data[key]) > 0:
                    writestr += json.dumps(self.data[key]) + "\n"
                fp.write(writestr)
                fp.write(seq)
