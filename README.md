# The Typing of The Dead: Overkill - DLC Dictionary Extractor

This is a Python script which extracts words and phrases from DLC dictionary files for [The Typing of The Dead: Overkill](https://en.wikipedia.org/wiki/The_House_of_the_Dead%3A_Overkill).

## Usage

To extract the file `dlc_dictionaries_profanityrules.pc`, run the following command:

```
python3 read_dlc_dictionary.py dlc_dictionaries_profanityrules.pc
```

Multiple filenames can be passed at once.

The above will create `dlc_dictionaries_profanityrules_phrases.txt` in the same directory. Sample output from this file:

```
------------------------------------------
Group Name -> Phrase
------------------------------------------
Ladybits -> Lady garden
Ladybits -> Axe-wound
Ladybits -> Barking spider
Ladybits -> Bearded clam
Ladybits -> Beef curtains
Ladybits -> Birth cannon
```

Phrases are always accompanied by a group name.
