-- Crea la base de datos Miau Market (idempotente)
-- Ejecutar primero o dejar que Django/migrate lo use via DB_NAME en .env

CREATE DATABASE IF NOT EXISTS miau_market
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE miau_market;

SELECT DATABASE() AS base_de_datos_activa;
