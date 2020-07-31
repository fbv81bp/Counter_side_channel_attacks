-- AND function calculation between an _odd_ number of XOR masked data shares
-- for every i this algorithm calculates:
-- Ci = [XOR(k/=i: Ak) AND XOR(j/=i: Bj)] XOR (Ai AND Bi)

-- This implementation calculates the output asynchronously in parallel. May need registers
-- against glitching.

-- The generic parameters enable arbitrary wide words to be AND-ed which consist of arbitrary odd
-- number masked shares. The algorithm does not work with an even number of shares due to its math
-- properties!

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use IEEE.std_logic_unsigned.all;

entity masked_AND is
    Generic ( shares : integer := 5;
              width : integer := 32);
    Port ( a_shares : in STD_LOGIC_VECTOR (shares*width-1 downto 0) := x"67978544a6f328ab1e12eae9c9876d3e60745557"; --testing...
           b_shares : in STD_LOGIC_VECTOR (shares*width-1 downto 0) := x"6abdc744895728abfe45c8d69db59cccd4284a07"; --testing...
           c_shares : out STD_LOGIC_VECTOR (shares*width-1 downto 0));-- 7297b766503779eb3617d9c400870c1c40306a37 okay
end masked_AND;

architecture Behavioral of masked_AND is

    type sharesT is array (shares-1 downto 0) of std_logic_vector(width-1 downto 0);
    signal as, bs, cs, andAB : sharesT;
    type sumT is array (shares-1 downto 0) of sharesT;
    signal sumA, sumB : sumT;
    
begin

in_gen: for i in 0 to shares-1 generate
    as(i) <= a_shares((i+1)*width-1 downto i*width);
    bs(i) <= b_shares((i+1)*width-1 downto i*width);
end generate;

gen_shares: for i in 0 to shares-1 generate
    andAB(i) <= as(i) and bs(i);
    gen_sums: for j in 0 to shares-3 generate
        cond0: if i = j generate
            sumA(i)(j) <= sumA(i)(j+1);
            sumB(i)(j) <= sumB(i)(j+1);
        end generate; 
        cond1: if i /= j generate
            sumA(i)(j) <= sumA(i)(j+1) xor as(j);
            sumB(i)(j) <= sumB(i)(j+1) xor bs(j);
        end generate; 
        sumA(i)(shares-2) <= as(shares-1) xor as(shares-2) when i < shares-2 else
                             as(shares-1)                  when i < shares-1 else
                             as(shares-2);
        sumB(i)(shares-2) <= bs(shares-1) xor bs(shares-2) when i < shares-2 else
                             bs(shares-1)                  when i < shares-1 else
                             bs(shares-2);
    end generate;
    cs(i) <= (sumA(i)(0) and sumB(i)(0)) xor andAB(i);
end generate;

out_gen: for i in 0 to shares-1 generate
    c_shares((i+1)*width-1 downto i*width) <= cs(i);
end generate;

end Behavioral;
