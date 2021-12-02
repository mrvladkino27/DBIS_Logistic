BEGIN;


CREATE TABLE public."Department"
(
    adress character varying(256) NOT NULL,
    PRIMARY KEY (adress)
);

CREATE TABLE public."User"
(
    "e-mail" character varying(64) NOT NULL,
    password character varying(64) NOT NULL,
    name character varying(64),
    department character varying(256) NOT NULL,
    role character varying(32) NOT NULL,
    PRIMARY KEY ("e-mail")
);

CREATE TABLE public."Distance"
(
    first_dep character varying(256) NOT NULL,
    second_dep character varying(256) NOT NULL,
    distance integer NOT NULL,
    PRIMARY KEY (first_dep, second_dep)
);

CREATE TABLE public."Order"
(
    id bigint NOT NULL,
    sender character varying(64) NOT NULL,
    reciever character varying(64) NOT NULL,
    send_dep character varying(256) NOT NULL,
    recieve_dep character varying(256) NOT NULL,
    size character varying(4) NOT NULL,
    status boolean NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public."User"
    ADD FOREIGN KEY (department)
    REFERENCES public."Department" (adress)
    NOT VALID;


ALTER TABLE public."Distance"
    ADD FOREIGN KEY (first_dep)
    REFERENCES public."Department" (adress)
    NOT VALID;


ALTER TABLE public."Distance"
    ADD FOREIGN KEY (second_dep)
    REFERENCES public."Department" (adress)
    NOT VALID;


ALTER TABLE public."Order"
    ADD FOREIGN KEY (sender)
    REFERENCES public."User" ("e-mail")
    NOT VALID;


ALTER TABLE public."Order"
    ADD FOREIGN KEY (reciever)
    REFERENCES public."User" ("e-mail")
    NOT VALID;


ALTER TABLE public."Order"
    ADD FOREIGN KEY (send_dep)
    REFERENCES public."Department" (adress)
    NOT VALID;


ALTER TABLE public."Order"
    ADD FOREIGN KEY (recieve_dep)
    REFERENCES public."Department" (adress)
    NOT VALID;

END;