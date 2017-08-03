USE tim_db;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS lab;
DROP TABLE IF EXISTS docker_image;
DROP TABLE IF EXISTS container;
DROP TABLE IF EXISTS host;

CREATE TABLE IF NOT EXISTS lab (
	l_code   			CHAR(4) NOT NULL PRIMARY KEY,
	l_gpu_quota 		INT,
	l_afns_quota 		BIGINT, -- Tera Byte
	l_afnn_quota 		BIGINT  -- Tera Byte
);

CREATE TABLE IF NOT EXISTS docker_image(
	d_name			VARCHAR(32) NOT NULL PRIMARY KEY, -- including version tag
	d_framework 		VARCHAR(32),
	d_dockerfile_path 	VARCHAR(256),
	d_start_command		VARCHAR(64),
	d_desc			VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS host (
	h_name  		VARCHAR(32) NOT NULL PRIMARY KEY,
	h_ip    		CHAR(16) NOT NULL,
	h_env_map		VARCHAR(1024),
	CHECK (h_env_map IS NULL or JSON_VALID(h_env_map))
);

CREATE TABLE IF NOT EXISTS user (
	u_id 			CHAR(8) NOT NULL PRIMARY KEY, -- company number
	u_name 			VARCHAR(32),
	l_code 			CHAR(4) NOT NULL,
	u_contact_number 	CHAR(12),
	u_email			VARCHAR(32),
	u_num			CHAR(4)
);
ALTER TABLE user ADD FOREIGN KEY (l_code) REFERENCES lab(l_code) ON UPDATE CASCADE ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS container (
	c_name 		    	VARCHAR(32) NOT NULL,
	c_gpu_idxes 		VARCHAR(128),
	c_env_map 	    	VARCHAR(1024),
	u_id 		    	CHAR(8) NOT NULL,
	d_name 		    	VARCHAR(32) NOT NULL,
	h_name 		    	VARCHAR(32) NOT NULL,
	PRIMARY KEY (c_name, h_name),
	CHECK (c_env_map IS NULL or JSON_VALID(c_env_map))
);
ALTER TABLE container ADD ports VARCHAR(256) AS (JSON_QUERY(c_env_map, '$.ports'));
ALTER TABLE container ADD extra_vols VARCHAR(256) AS (JSON_QUERY(c_env_map, '$.extra_vols'));
ALTER TABLE host ADD gpus VARCHAR(256) AS (JSON_QUERY(h_env_map, '$.gpus'));
ALTER TABLE container ADD FOREIGN KEY (u_id) REFERENCES user(u_id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE container ADD FOREIGN KEY (d_name) REFERENCES docker_image(d_name) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE container ADD FOREIGN KEY (h_name) REFERENCES host(h_name) ON UPDATE CASCADE ON DELETE CASCADE;
