# on host run postgres as a container. 
$sudo docker run -v /home/app/rookie/sql/:/sql --rm -t -i --link pg_test:pg eg_postgresql bash

# then "link" to this container
$sudo docker run -v /home/app/rookie/sql/:/sql --rm -t -i --link pg_test:pg eg_postgresql bash

# this will give you a continer prompt for a user="postgres". Here PG is an alias of some kind to link to ports.
# see https://github.com/wsargent/docker-cheat-sheet#links
$postgres@68ef5446cc49:/$ createuser -U docker -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT -s rookie -P

# from that prompt, make a postgres user, rookie
$postgres@68ef5446cc49:/$ createuser -U docker -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT -s rookie -P

# then make a db, rookie
$postgres@68ef5446cc49:/$ createdb -O rookie rookie -U rookie -h $PG_PORT_5432_TCP_ADDR -p $PG_PORT_5432_TCP_PORT 

