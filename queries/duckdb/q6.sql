-- Q6
 select
         sum(l_extendedprice * l_discount) as revenue
 from
         lineitem
 where
         l_shipdate >= date '1997-01-01'
         and l_shipdate < date '1997-01-01' + interval '1 years'
         and l_discount between 0.06 and 0.08
         and l_quantity < 24;
