create view county_winners as
select  
       case when a.candidate = 'HILLARY CLINTON' then 1
            when a.candidate = 'BERNIE SANDERS' then 2
            when a.candidate = 'MARTIN O''MALLEY' then 3
            else 4 end candidate
     , cast(c.fips as integer) state_fips
     , cast(a.county_fips as integer) county_fips
     , cast(a.fraction_votes as float) vote_pct
     , cast(b.age135214 as float) under_5yo_pct
     , cast(b.age295214 as float) under_18yo_pct
     , cast(b.age775214 as float) over_65yo_pct
     , cast(b.pop060210 as float) pop_density
from (
	select
	    fips county_fips
	  , trim(upper(candidate)) candidate
	  , trim(upper(state)) state
	  , fraction_votes
	  , dense_rank() over (
	  		partition by fips, party
	  		order by fraction_votes desc
	  ) county_place
	from primary_results 
	where party = 'Democrat'
	and candidate not in (' No Preference', ' Uncommitted') and fips is not null
) a 
left join county_facts b on a.county_fips = b.fips
left join county_facts c on a.state = upper(trim(c.area_name))
where a.county_place = 1
  and b.age135214 is not null
  and b.age295214 is not null
  and b.age775214 is not null
  and b.pop060210 is not null
  and a.fraction_votes is not null;
;