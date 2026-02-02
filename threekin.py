import math
from fractions import Fraction
from itertools import product

def get_log_fractional_part(number):
    """
    Calculates the fractional part of log2(number).
    Mathematically: {x} = x - floor(x).
    In Python: x % 1 handles this correctly for negative logs too.
    """
    val = math.log2(number)
    return val % 1

#PRIMES = [2, 3, 5, 7, 11, 13]
def pf(num: int):
    twos = 0
    threes = 0
    fives = 0
    sevens = 0
    elevens = 0
    thirteens = 0
    while num % 2 == 0:
        num /= 2
        twos += 1
    while num % 3 == 0:
        num /= 3
        threes += 1
    while num % 5 == 0:
        num /= 5
        fives += 1
    while num % 7 == 0:
        num /= 7
        sevens += 1
    while num % 11 == 0:
        num /= 11
        elevens += 1
    while num % 13 == 0:
        num /= 13
        thirteens += 1
    return (twos, threes, fives, sevens, elevens, thirteens)

three_names = { 1: "chy", 2:"scy",    3:"xcy",  4: "cvachy",  5: "dachy",  6: "tuichy",  7: "sachy",  8: "chlachy",  9: "yuchy",  10: "xychy", 11: "nuichy", 12: "kychy", 
               -1: "fu", -2: "schu", -3: "ju", -4: "cvafu",  -5: "dafu",  -6: "tuifu",  -7: "safu",  -8: "chlafu",  -9: "yufu",  -10: "xyfu", -11: "nuifu", -12: "kyfu"}
five_names = {1: "ly", 2:"dry", 3:"drvy", 4: "cvaly", 5: "daly", 6:"tuily", 7: "saly", 8: "chlaly", 9: "yuly", 10: "xyly", 11: "nuily", 12: "kyly",
              -1: "su", -2: "sru", -3: "srvu", -4: "cvasu", -5: "dasu", -6: "tuisu", -7: "sasu", -8: "chlasu", -9: "yusu", -10: "xysu", -11: "nuisu", -12: "kysu"}
seven_names = {1: "my", 2:"mry", 3:"mrvy", 4: "cvamy", 5: "damy", 6:"tuimy", 7: "samy", 8: "chlamy", 9: "yumy", 10: "xymy", 11: "nuimy", 12: "kymy",
              -1: "pu", -2: "pru", -3: "prvu", -4: "cvapu", -5: "dapu", -6: "tuipu", -7: "sapu", -8: "chlapu", -9: "yupu", -10: "xypu", -11: "nuipu", -12: "kypu"}
eleven_names = {1: "zy", 2:"zry", 3:"zrvy", 4: "cvazy", 5: "dazy", 6:"tuizy", 7: "sazy", 8: "chlazy", 9: "yuzy", 10: "xyzy", 11: "nuizy", 12: "kyzy",
              -1: "ku", -2: "kru", -3: "krvu", -4: "cvaku", -5: "daku", -6: "tuiku", -7: "saku", -8: "chlaku", -9: "yuku", -10: "xyku", -11: "nuiku", -12: "kyku"}
thirteen_names = {1: "gnay", 2:"gray", 3:"grvay", 4: "cvagnay", 5: "dagnay", 6:"tuignay", 7: "sagnay", 8: "chlagnay", 9: "yugnay", 10: "xygnay", 11: "nuignay", 12: "kygnay",
              -1: "gnau", -2: "grau", -3: "grvau", -4: "cvagnau", -5: "dagnau", -6: "tuignau", -7: "sagnau", -8: "chlagnau", -9: "yugnau", -10: "xygnau", -11: "nuignau", -12: "kygnau"}

names = [None, three_names, five_names, seven_names, eleven_names, thirteen_names]

def name_ratio(ratio: Fraction):
    try:
        numerator = pf(ratio.numerator)
        denominator = pf(ratio.denominator)
        combined_factors = [0, 0, 0, 0, 0, 0]
        for i in range(6):
            combined_factors[i] = combined_factors[i] + numerator[i] - denominator[i]
        num_primes = 0
        name = ""
        for i in range(1, 6):
            if combined_factors[i] != 0:
                num_primes += 1
                name += names[i][combined_factors[i]]
        
        if num_primes > 1:
            if name[-1] == "u":
                name = name[:-1]
            if name[-1] == "y":
                name = name[:-1] + "i"
        if num_primes == 0:
            name = "ah"
        
        name = name.title()
        return name.strip()
    except Exception:
        return "???"

def format_exponents(a, b, c, d, e):
    """Helper to pretty-print the factorization."""
    parts = []
    if a != 0: parts.append(f"3^({a})")
    if b != 0: parts.append(f"5^({b})")
    if c != 0: parts.append(f"7^({c})")
    if d != 0: parts.append(f"11^({d})")
    if e != 0: parts.append(f"13^({d})")
    return "*".join(parts) if parts else "1"

def main():
    # Store tuples of (fractional_part_of_log, exact_fraction, exponents_tuple)
    results = []

    # The sum of absolute values is at most 3, so no single exponent
    # can exceed 3 or be less than -3.
    r = range(-5, 6)

    # Generate all combinations of exponents
    for a, b, c, d, e in product(r, repeat=5):
        
        # Check the constraint: |a| + |b| + |c| + |d| <= 3
        if abs(a) + abs(b) + abs(c) + abs(d) + abs(e) <= 5 and e == 0:
            
            # Calculate the exact fraction value
            # numerators get positive exponents, denominators get negative ones
            numerator = (3**max(0, a)) * (5**max(0, b)) * (7**max(0, c)) * (11**max(0, d)) * (13**max(0, e))
            denominator = (3**max(0, -a)) * (5**max(0, -b)) * (7**max(0, -c)) * (11**max(0, -d)) * (13**max(0, -e))
            
            fraction_val = Fraction(numerator, denominator)
            two_factor = -int(math.floor(math.log(fraction_val, 2)))
            fraction_val *= Fraction(2)**two_factor
            
            # Calculate the sort key
            sort_key = get_log_fractional_part(fraction_val)
            
            results.append({
                'key': sort_key,
                'fraction': fraction_val,
                'exponents': (a, b, c, d, e)
            })

    # Sort the results by the fractional part of the log
    results.sort(key=lambda x: x['key'])

    # Print the results
    print(f"{'IDX':<5} | {'LOG2 MOD 1':<12} | {'FRACTION':<15} | {'FACTORIZATION'}")
    print("-" * 60)
    
    with open("output.txt", "w") as f:
        for i, item in enumerate(results):
            # We limit the output to the first 20 and last 5 for brevity in this run,
            # but you can remove the slice to see all of them.
            fact_str = name_ratio(item['fraction'])
            edo_equivalent = round(41*math.log(item['fraction'], 2))
            f.write(f"{i:<5} | {item['key']:.6f}       | {str(item['fraction']):<15} | {fact_str:<15} | {edo_equivalent} \n")

if __name__ == "__main__":
    main()