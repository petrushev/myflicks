SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

CREATE OR REPLACE PROCEDURAL LANGUAGE plpythonu;

ALTER PROCEDURAL LANGUAGE plpythonu OWNER TO postgres;

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE movie (
    id integer NOT NULL,
    title character varying(1023) NOT NULL,
    url character varying(2047) NOT NULL,
    meta json,
    CONSTRAINT ch_movie_url CHECK ((((url)::text !~~ '%://'::text) AND (((url)::text ~~* 'http://%'::text) OR ((url)::text ~~* 'https://%'::text))))
);

ALTER TABLE public.movie OWNER TO postgres;

CREATE SEQUENCE movie_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.movie_id_seq OWNER TO postgres;

ALTER SEQUENCE movie_id_seq OWNED BY movie.id;

CREATE TABLE rating (
    user_id integer NOT NULL,
    movie_id integer NOT NULL,
    rating smallint NOT NULL,
    rated timestamp without time zone NOT NULL,
    CONSTRAINT ch_rating CHECK (((rating >= 0) AND (rating <= 10)))
);

ALTER TABLE public.rating OWNER TO postgres;

CREATE TABLE "user" (
    id integer NOT NULL,
    nickname character varying(128) NOT NULL,
    service character varying(8) NOT NULL,
    fullname character varying(128),
    email character varying(64)
);

ALTER TABLE public."user" OWNER TO postgres;

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.user_id_seq OWNER TO postgres;

ALTER SEQUENCE user_id_seq OWNED BY "user".id;

ALTER TABLE ONLY movie ALTER COLUMN id SET DEFAULT nextval('movie_id_seq'::regclass);

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);

SELECT pg_catalog.setval('movie_id_seq', 1, false);

SELECT pg_catalog.setval('user_id_seq', 1, true);

ALTER TABLE ONLY movie
    ADD CONSTRAINT p_movie PRIMARY KEY (id);

ALTER TABLE ONLY rating
    ADD CONSTRAINT p_rating PRIMARY KEY (user_id, movie_id);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT p_user PRIMARY KEY (id);

ALTER TABLE ONLY movie
    ADD CONSTRAINT u_movie UNIQUE (title);

ALTER TABLE ONLY movie
    ADD CONSTRAINT u_movie_url UNIQUE (url);

ALTER TABLE ONLY "user"
    ADD CONSTRAINT u_user UNIQUE (nickname, service);

ALTER TABLE ONLY rating
    ADD CONSTRAINT fk_rating_movie FOREIGN KEY (movie_id) REFERENCES movie(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY rating
    ADD CONSTRAINT fk_rating_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE RESTRICT;

-- restructured movie table
delete from rating;
delete from movie;

ALTER TABLE movie
  DROP CONSTRAINT u_movie;
ALTER TABLE movie
  DROP CONSTRAINT u_movie_url;
ALTER TABLE movie
  DROP CONSTRAINT ch_movie_url;
ALTER TABLE movie
  DROP COLUMN url;
ALTER TABLE movie
  ADD COLUMN imdbid character varying(31);
ALTER TABLE movie
  ADD COLUMN year smallint NOT NULL;
ALTER TABLE movie
  ADD CONSTRAINT u_movie UNIQUE (title, year);

ALTER TABLE movie
  ADD COLUMN img text;

-- added custom query indexes

CREATE INDEX CONCURRENTLY i_rating_rated
  ON rating USING btree
  (rated);
CREATE INDEX CONCURRENTLY i3_movie
  ON movie USING gist
  ((' '||title) COLLATE pg_catalog."default" gist_trgm_ops);
