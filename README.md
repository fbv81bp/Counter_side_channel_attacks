# Side channel attack countermeasures

* masked_AND_by_me contains paramaterizable code to calculate "AND" between arbitrary many masked shares of two words of arbitrary bit widths. I discovered this function while studiing side channel attacks. It has NOT been proven SCA proof!! The function calculates Ci-s by "AND"-ing the corresponding bits Ai and Bi, and correcting this with the parities of all the other bits Aj and Bj, where j<>i by "AND"-ing the parities and XOR-ing this to the Ai&Bi product.
* sub_box_masking contains code for creating RAM based substitution for first and multiple order sharing in a way that the required RAM doesn't grow exponentially with the number of shares used. Again, this is yet another research result of mine, and has NOT been proven SCA proof!!
