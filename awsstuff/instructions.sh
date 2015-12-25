# on host run postgres as a container. 
$docker run -d -P --name pg_test eg_postgresql

# then "link" to this container
$sudo docker run -v /home/app/rookie/sql/:/sql --rm -t -i --link pg_test:pg eg_postgresql bash

# this will give you a continer prompt for a user="postgres". Here PG is an alias of some kind to link to ports.
# see https://github.com/wsargent/docker-cheat-sheet#links
$postgres@68ef5446cc49:/$ createuser -U docker -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT -s rookie -P

# from that prompt, make a postgres user, rookie
$postgres@68ef5446cc49:/$ createuser -U docker -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT -s rookie -P

# then make a db, rookie
$postgres@68ef5446cc49:/$ createdb -O rookie rookie -U rookie -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT 

# then add indexing to speed up snippet making 10X
# you run this stuff from a pg prompt --> 

# create extension pg_trgm;
# CREATE EXTENSION
# create index test_trgm_gin on sentences using gin (text gin_trgm_ops);
## http://www.depesz.com/2011/02/19/waiting-for-9-1-faster-likeilike/

# to test it is working
#$ psql -d rookie -U rookie -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT
