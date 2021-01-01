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

entity masked_AND_reg_non_complete is
    Generic ( shares : integer := 5;
              width : integer := 32);
    Port ( --clock, load: in std_logic; --uncomment for synthesis!
           a_shares : in STD_LOGIC_VECTOR (shares*width-1 downto 0) := x"67978544a6f328ab1e12eae9c9876d3e60745557";
           b_shares : in STD_LOGIC_VECTOR (shares*width-1 downto 0) := x"6abdc744895728abfe45c8d69db59cccd4284a07";
           c_shares : out STD_LOGIC_VECTOR (shares*width-1 downto 0));
end masked_AND_reg_non_complete;

architecture Behavioral of masked_AND_reg_non_complete is

    signal a_and, b_and, a_par, b_par, cs : STD_LOGIC_VECTOR (shares*width-1 downto 0);
	constant offset : integer := 1;
	
--testing... comment for synthesis!
    signal clock, load : std_logic := '0';
    signal absum, csum : std_logic_vector(width-1 downto 0);
    
begin

    process(clock)
        variable andABbit, parAbit, parBbit : std_logic;
    begin
        if rising_edge(clock) then
            if load = '1' then
                a_par <= a_shares;
                b_par <= b_shares;
                cs <= (others => 'W');
            else
                a_par <= a_par(a_par'high-1 downto 0) & a_par(a_par'high);
                b_par <= b_par(b_par'high-1 downto 0) & b_par(b_par'high);
                andABbit := a_and(a_and'high) and b_and(b_and'high);
                parAbit := a_par(a_par'high-width);
                parBbit := b_par(b_par'high-width);
                for i in 2 to shares-1 loop
                    parAbit := parAbit xor a_par(a_par'high-i*width);
                    parBbit := parBbit xor b_par(b_par'high-i*width);
                end loop;
                cs  <= cs(cs'high-1 downto 0) & ((parAbit and parBbit) xor andABbit);
            end if;
        end if;
    end process;

	a_and <= a_par(a_par'high-offset*width downto 0) & a_par(a_par'high downto a_par'high-offset*width+1);
	b_and <= b_par(b_par'high-offset*width downto 0) & b_par(b_par'high downto b_par'high-offset*width+1);
   
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

    process(a_shares, b_shares, cs)
        variable a_shares_sum, b_shares_sum, c_shares_sum : std_logic_vector(width-1 downto 0);
    begin
        a_shares_sum := (others => '0');
        b_shares_sum := (others => '0');
        c_shares_sum := (others => '0');
        for i in 1 to shares loop
            a_shares_sum := a_shares_sum xor a_shares(i*width-1 downto (i-1)*width);
            b_shares_sum := b_shares_sum xor b_shares(i*width-1 downto (i-1)*width);
            c_shares_sum := c_shares_sum xor cs(i*width-1 downto (i-1)*width);
        end loop;
        absum <= a_shares_sum and b_shares_sum; -- expected x"54007162"
        csum <= c_shares_sum; -- x"54007162" okay
    end process;
    
end Behavioral;
