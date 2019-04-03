CREATE TABLE user_table(
   username CHAR(50) PRIMARY KEY NOT NULL,
   password CHAR(50) NOT NULL,
   fingerprint BLOB
);

CREATE TABLE QRcode_table(
   encode_data CHAR(500) PRIMARY KEY NOT NULL,
   data CHAR(500) NOT NULL
);
