BEGIN;


CREATE TABLE public."department"
(
    adress character varying(256) NOT NULL,
    PRIMARY KEY (adress)
);

CREATE TABLE public."user"
(
    email character varying(64) NOT NULL,
    password character varying(64) NOT NULL,
    name character varying(64),
    department character varying(256) NOT NULL,
    role character varying(32) NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE public."distance"
(
    first_dep character varying(256) NOT NULL,
    second_dep character varying(256) NOT NULL,
    distance integer NOT NULL,
    PRIMARY KEY (first_dep, second_dep)
);

CREATE TABLE public."order"
(
    id bigint NOT NULL,
    sender character varying(64) NOT NULL,
    reciever character varying(64) NOT NULL,
    send_dep character varying(256) NOT NULL,
    recieve_dep character varying(256) NOT NULL,
    size integer NOT NULL,
    status boolean NOT NULL,
    price numeric(5, 2) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE public."user"
    ADD FOREIGN KEY (department)
    REFERENCES public."department" (adress)
    NOT VALID;


ALTER TABLE public."distance"
    ADD FOREIGN KEY (first_dep)
    REFERENCES public."department" (adress)
    NOT VALID;


ALTER TABLE public."distance"
    ADD FOREIGN KEY (second_dep)
    REFERENCES public."department" (adress)
    NOT VALID;


ALTER TABLE public."order"
    ADD FOREIGN KEY (sender)
    REFERENCES public."user" (email)
    NOT VALID;


ALTER TABLE public."order"
    ADD FOREIGN KEY (reciever)
    REFERENCES public."user" (email)
    NOT VALID;


ALTER TABLE public."order"
    ADD FOREIGN KEY (send_dep)
    REFERENCES public."department" (adress)
    NOT VALID;


ALTER TABLE public."order"
    ADD FOREIGN KEY (recieve_dep)
    REFERENCES public."department" (adress)
    NOT VALID;

END;