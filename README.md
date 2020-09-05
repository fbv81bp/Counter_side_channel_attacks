# Side channel attack countermeasures

* masked_AND_by_me.py contains paramaterizable code to calculate "AND" between arbitrary many masked shares of two words of arbitrary bit widths. I discovered this function while studiing side channel attacks. It has NOT been proven SCA proof!! The function calculates Ci-s by "AND"-ing the corresponding bits Ai and Bi, and correcting this with the parities of all the other bits Aj and Bj, where j<>i by "AND"-ing the parities and XOR-ing this to the Ai&Bi product.

Its advantage is that it shouldn't need new random input data, and still the computations and the output should be safely masked. However the versions with offsets may generate more algorithmic noise if the offstes are randomized:

* and_offset.py may already be SCA proof, in fact it hopefully is a threshold implementation, with more or less randomly shufflable computations - these make analysis more noisy, if the attacker doesn't know which piece of trace belongs to which share, and thus has to sum up some trace pieces, like if they were implemented in parallel hardware and calculate with those algorithmically noisy results.

* and_offset_rolling.py implements a the previous offseted version a little bit simplified based on the fact that parity is like a "rolling hash", which can be updated element wise, and doesn't need the full recomputation for each AND-ed bit's corrections.
