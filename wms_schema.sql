--
-- PostgreSQL database dump
--

\restrict D9VDCYhE5P8xaj16chwr4d12BXrDyqp18ENThFcsROPnag9a3NlspDMREdntoQg

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: inventory; Type: TABLE; Schema: public; Owner: wms_user
--

CREATE TABLE public.inventory (
    product_id bigint NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT check_inventory_quantity_positive CHECK ((quantity >= 0))
);


ALTER TABLE public.inventory OWNER TO wms_user;

--
-- Name: products; Type: TABLE; Schema: public; Owner: wms_user
--

CREATE TABLE public.products (
    product_id bigint NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    price double precision NOT NULL,
    CONSTRAINT check_product_price_positive CHECK ((price >= (0)::double precision))
);


ALTER TABLE public.products OWNER TO wms_user;

--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: wms_user
--

CREATE SEQUENCE public.products_product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_product_id_seq OWNER TO wms_user;

--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wms_user
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: wms_user
--

CREATE TABLE public.warehouses (
    warehouse_id integer NOT NULL,
    location character varying(200) NOT NULL
);


ALTER TABLE public.warehouses OWNER TO wms_user;

--
-- Name: warehouses_warehouse_id_seq; Type: SEQUENCE; Schema: public; Owner: wms_user
--

CREATE SEQUENCE public.warehouses_warehouse_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouses_warehouse_id_seq OWNER TO wms_user;

--
-- Name: warehouses_warehouse_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wms_user
--

ALTER SEQUENCE public.warehouses_warehouse_id_seq OWNED BY public.warehouses.warehouse_id;


--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: wms_user
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: warehouses warehouse_id; Type: DEFAULT; Schema: public; Owner: wms_user
--

ALTER TABLE ONLY public.warehouses ALTER COLUMN warehouse_id SET DEFAULT nextval('public.warehouses_warehouse_id_seq'::regclass);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: wms_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (product_id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: wms_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: wms_user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (warehouse_id);


--
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: wms_user
--

CREATE INDEX ix_products_name ON public.products USING btree (name);


--
-- Name: ix_warehouses_location; Type: INDEX; Schema: public; Owner: wms_user
--

CREATE UNIQUE INDEX ix_warehouses_location ON public.warehouses USING btree (location);


--
-- Name: inventory inventory_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wms_user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- PostgreSQL database dump complete
--

\unrestrict D9VDCYhE5P8xaj16chwr4d12BXrDyqp18ENThFcsROPnag9a3NlspDMREdntoQg

