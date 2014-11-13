#!/usr/bin/env python
from math import sqrt
 
def pearson(pairs):
    # Takes in a list of pairwise ratings and produces a pearson similarity
    series_1 = [float(pair[0]) for pair in pairs]
    series_2 = [float(pair[1]) for pair in pairs]
 
    sum1 = sum(series_1)
    sum2 = sum(series_2)
 
    squares1 = sum([ n*n for n in series_1 ])
    squares2 = sum([ n*n for n in series_2 ])
 
    product_sum = sum([ n * m for n,m in pairs ])
 
    size = len(pairs)
 
    numerator = product_sum - ((sum1 * sum2)/size)
    denominator = sqrt((squares1 - (sum1*sum1) / size) * (squares2 - (sum2*sum2)/size))
 
    if denominator == 0:
        return 0
    
    return numerator/denominator