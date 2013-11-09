SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

CREATE OR REPLACE PROCEDURAL LANGUAGE plpythonu;

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';

SET search_path = public, pg_catalog;

CREATE FUNCTION json_select(data json, path text[]) RETURNS json
    LANGUAGE plpythonu IMMUTABLE
    AS $$
if data is None:
    return None
from json import loads, dumps
data_ = loads(data)
path_ = list(path)
while path_:
    key = path_.pop(0)
    try:
        data_ = data_[key]
    except (IndexError, KeyError):
        return None
return dumps(data_)
$$;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE movie (
    id integer NOT NULL,
    title character varying(1023) NOT NULL,
    meta json,
    imdbid character varying(31),
    year smallint NOT NULL,
    img text
);

CREATE SEQUENCE movie_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE movie_id_seq OWNED BY movie.id;

CREATE TABLE rating (
    user_id integer NOT NULL,
    movie_id integer NOT NULL,
    rating smallint NOT NULL,
    rated timestamp without time zone NOT NULL,
    CONSTRAINT ch_rating CHECK (((rating >= 0) AND (rating <= 10)))
);

CREATE TABLE "user" (
    id integer NOT NULL,
    nickname character varying(128) NOT NULL,
    service character varying(8) NOT NULL,
    fullname character varying(128),
    email character varying(64)
);

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE user_id_seq OWNED BY "user".id;

CREATE TABLE watchlist (
    user_id integer NOT NULL,
    movie_id integer NOT NULL
);

ALTER TABLE ONLY movie ALTER COLUMN id SET DEFAULT nextval('movie_id_seq'::regclass);

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);

ALTER TABLE ONLY movie
    ADD CONSTRAINT p_movie PRIMARY KEY (id);

ALTER TABLE ONLY rating
    ADD CONSTRAINT p_rating PRIMARY KEY (user_id, movie_id);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT p_user PRIMARY KEY (id);

ALTER TABLE ONLY watchlist
    ADD CONSTRAINT p_watchlist PRIMARY KEY (user_id, movie_id);

ALTER TABLE ONLY movie
    ADD CONSTRAINT u_movie UNIQUE (title, year);

ALTER TABLE ONLY rating
    ADD CONSTRAINT u_rating_movie_rated UNIQUE (movie_id, rated);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT u_user UNIQUE (nickname, service);

CREATE INDEX i3_movie ON movie USING gist (((' '::text || (title)::text)) gist_trgm_ops);

CREATE INDEX i3_movie_2 ON movie USING gist ((((' '::text || lower((title)::text)) || ' '::text)) gist_trgm_ops);

CREATE INDEX i3_movie_actor ON movie USING gist (btrim((json_select(meta, '{Actors}'::text[]))::text, '"'::text) gist_trgm_ops) WHERE (meta IS NOT NULL);

CREATE INDEX i3_movie_director ON movie USING gist (btrim((json_select(meta, '{Director}'::text[]))::text, '"'::text) gist_trgm_ops) WHERE (meta IS NOT NULL);

CREATE INDEX i3_movie_screenwriter ON movie USING gist (btrim((json_select(meta, '{Writer}'::text[]))::text, '"'::text) gist_trgm_ops) WHERE (meta IS NOT NULL);

CREATE INDEX i_rating_rated ON rating USING btree (rated);

ALTER TABLE ONLY rating
    ADD CONSTRAINT fk_rating_movie FOREIGN KEY (movie_id) REFERENCES movie(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY rating
    ADD CONSTRAINT fk_rating_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY watchlist
    ADD CONSTRAINT fk_watchlist_movie FOREIGN KEY (movie_id) REFERENCES movie(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY watchlist
    ADD CONSTRAINT fk_watchlist_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE RESTRICT;
