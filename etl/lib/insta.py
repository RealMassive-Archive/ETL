"""
This file replicates the instagram id generator proposed in this article:

http://instagram-engineering.tumblr.com/post/10853187575/sharding-ids-at-instagram


CREATE OR REPLACE FUNCTION insta5.next_id(OUT result bigint) AS $$
DECLARE
    our_epoch bigint := 1314220021721;
    seq_id bigint;
    now_millis bigint;
    shard_id int := 5;
BEGIN
    SELECT nextval('insta5.table_id_seq') %% 1024 INTO seq_id;

    SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000) INTO now_millis;
    result := (now_millis - our_epoch) << 23;
    result := result | (shard_id << 10);
    result := result | (seq_id);
END;
$$ LANGUAGE PLPGSQL;
"""

from time import sleep, time


def get_now():
    """ IMPORTANT: the underlying system time of the machine running get_now
        must match the system time of the production postgres instance.
    """
    return int(time() * 1000)


class Sequence:
    def __init__(self):
        self.current = 0

    def nextval(self):
        self.current += 1
        return self.current


def next_id(seq):
    """ pure python, instagram next_id compatible id generator.

        WARNING: next_id can only generate 1024 unique ids per millisecond.
        python is slow enough that this should not be an issue.

        IMPORTANT: to use the ids in postgres successfully the postgres
        sequence MUST be altered to the final value of seq.current

        the actual postgres command will look like this:

        "ALTER SEQUENCE table_id_seq RESTART WITH {};".format(str(seq.current))
    """
    our_epoch = 1314220021721
    shard_id = 1
    seq_id = seq.nextval() % 1024
    now_millis = get_now()
    result = (now_millis - our_epoch) << 23
    result = result | (shard_id << 10)
    result = result | (seq_id)
    return result
