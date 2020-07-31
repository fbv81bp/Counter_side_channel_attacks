-- AND function calculation between an odd number of XOR masked data shares
-- for every i this algorithm calculates:
-- Ci = [XOR(k/=i: Ak) AND XOR(j/=i: Bj)] XOR (Ai AND Bi)

-- This implementation uses shift registers and calculates 1 single output bit at a clock cycle.

-- The generic parameters enable arbitrary wide words to be AND-ed which consist of arbitrary odd
-- number masked shares. The algorithm does not work with an even number of shares due to its math
-- properties!

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use IEEE.std_logic_unsigned.all;

entity masked_AND_reg is
    Generic ( shares : integer := 5;
              width : integer := 32);
    Port ( --clock, load: in std_logic; --uncomment for synthesis!
           a_shares : in STD_LOGIC_VECTOR (shares*width-1 downto 0) := x"67978544a6f328ab1e12eae9c9876d3e60745557";
           b_shares : in STD_LOGIC_VECTOR (shares*width-1 downto 0) := x"6abdc744895728abfe45c8d69db59cccd4284a07";
           c_shares : out STD_LOGIC_VECTOR (shares*width-1 downto 0));-- 7297b766503779eb3617d9c400870c1c40306a37 expected
                                                                --result 7297b766503779eb3617d9c400870c1c40306a37 okay
end masked_AND_reg;

architecture Behavioral of masked_AND_reg is

    signal as, bs, cs : STD_LOGIC_VECTOR (shares*width-1 downto 0);

--testing... comment for synthesis!
    signal clock, load : std_logic := '0';

begin

    process(clock)
        variable andABbit, parAbit, parBbit : std_logic;
    begin
        if rising_edge(clock) then
            if load = '1' then
                as <= a_shares;
                bs <= b_shares;
                cs <= (others => 'W');
            else
                as <= as(as'high-1 downto 0) & as(as'high);
                bs <= bs(bs'high-1 downto 0) & bs(bs'high);
                andABbit := as(as'high) and bs(bs'high);
                parAbit := as(as'high-width);
                parBbit := bs(bs'high-width);
                for i in 2 to shares-1 loop
                    parAbit := parAbit xor as(as'high-i*width);
                    parBbit := parBbit xor bs(bs'high-i*width);
                end loop;
                cs  <= cs(cs'high-1 downto 0) & ((parAbit and parBbit) xor andABbit);
            end if;
        end if;
    end process;
    
    c_shares <= cs;

--testing... comment for synthesis!

    process begin
        wait for 5ns;
        clock <= not clock;
    end process;

    process begin
        wait for 50ns;
        load <= '1';
        wait for 10ns;
        load <= '0';
        wait;
    end process;

end Behavioral;
