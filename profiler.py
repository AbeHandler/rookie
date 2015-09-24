import pstats
p = pstats.Stats('profile')
p.strip_dirs().sort_stats('time').reverse_order().print_stats()
