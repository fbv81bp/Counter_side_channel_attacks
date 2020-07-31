# Side channel attack countermeasures

* masked_AND_by_me contains paramaterizable code to calculate "AND" between arbitrary many masked shares of two words of arbitrary bit widths. I discovered this function while studiing side channel attacks. It has NOT been proven SCA proof!! The function calculates Ci-s by "AND"-ing the corresponding bits Ai and Bi, and correcting this with the parities of all the other bits Aj and Bj, where j<>i by "AND"-ing the parities and XOR-ing this to the Ai&Bi product.
