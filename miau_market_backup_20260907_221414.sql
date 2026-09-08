-- Backup Miau Market
-- Fecha: 2026-09-07T22:14:14
-- Base: miau_market

CREATE DATABASE IF NOT EXISTS `miau_market` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `miau_market`;
SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `auth_group` vacia

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `auth_group_permissions_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `auth_group_permissions` vacia

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (21, 'Can add Token', 6, 'add_token');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (22, 'Can change Token', 6, 'change_token');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (23, 'Can delete Token', 6, 'delete_token');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (24, 'Can view Token', 6, 'view_token');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (25, 'Can add Token', 7, 'add_tokenproxy');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (26, 'Can change Token', 7, 'change_tokenproxy');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (27, 'Can delete Token', 7, 'delete_tokenproxy');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (28, 'Can view Token', 7, 'view_tokenproxy');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (29, 'Can add usuario', 8, 'add_usuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (30, 'Can change usuario', 8, 'change_usuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (31, 'Can delete usuario', 8, 'delete_usuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (32, 'Can view usuario', 8, 'view_usuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (33, 'Can add producto', 9, 'add_producto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (34, 'Can change producto', 9, 'change_producto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (35, 'Can delete producto', 9, 'delete_producto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (36, 'Can view producto', 9, 'view_producto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (37, 'Can add notificacion', 10, 'add_notificacion');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (38, 'Can change notificacion', 10, 'change_notificacion');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (39, 'Can delete notificacion', 10, 'delete_notificacion');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (40, 'Can view notificacion', 10, 'view_notificacion');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (41, 'Can add pedido', 11, 'add_pedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (42, 'Can change pedido', 11, 'change_pedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (43, 'Can delete pedido', 11, 'delete_pedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (44, 'Can view pedido', 11, 'view_pedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (45, 'Can add detalle pedido', 12, 'add_detallepedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (46, 'Can change detalle pedido', 12, 'change_detallepedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (47, 'Can delete detalle pedido', 12, 'delete_detallepedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (48, 'Can view detalle pedido', 12, 'view_detallepedido');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (49, 'Can add resena producto', 13, 'add_resenaproducto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (50, 'Can change resena producto', 13, 'change_resenaproducto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (51, 'Can delete resena producto', 13, 'delete_resenaproducto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (52, 'Can view resena producto', 13, 'view_resenaproducto');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (53, 'Can add Configuracion MiauBot', 14, 'add_miaubotconfig');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (54, 'Can change Configuracion MiauBot', 14, 'change_miaubotconfig');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (55, 'Can delete Configuracion MiauBot', 14, 'delete_miaubotconfig');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (56, 'Can view Configuracion MiauBot', 14, 'view_miaubotconfig');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (57, 'Can add miau bot conocimiento', 15, 'add_miaubotconocimiento');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (58, 'Can change miau bot conocimiento', 15, 'change_miaubotconocimiento');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (59, 'Can delete miau bot conocimiento', 15, 'delete_miaubotconocimiento');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (60, 'Can view miau bot conocimiento', 15, 'view_miaubotconocimiento');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (61, 'Can add miau bot frase', 16, 'add_miaubotfrase');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (62, 'Can change miau bot frase', 16, 'change_miaubotfrase');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (63, 'Can delete miau bot frase', 16, 'delete_miaubotfrase');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (64, 'Can view miau bot frase', 16, 'view_miaubotfrase');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (65, 'Can add Aprendizaje MiauBot', 17, 'add_miaubotaprendizaje');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (66, 'Can change Aprendizaje MiauBot', 17, 'change_miaubotaprendizaje');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (67, 'Can delete Aprendizaje MiauBot', 17, 'delete_miaubotaprendizaje');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (68, 'Can view Aprendizaje MiauBot', 17, 'view_miaubotaprendizaje');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (69, 'Can add Memoria MiauBot', 18, 'add_miaubotmemoriausuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (70, 'Can change Memoria MiauBot', 18, 'change_miaubotmemoriausuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (71, 'Can delete Memoria MiauBot', 18, 'delete_miaubotmemoriausuario');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (72, 'Can view Memoria MiauBot', 18, 'view_miaubotmemoriausuario');

DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`Id_User`),
  CONSTRAINT `auth_user_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `auth_user_groups` vacia

DROP TABLE IF EXISTS `auth_user_permissions`;
CREATE TABLE `auth_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `auth_user_permissions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`Id_User`),
  CONSTRAINT `auth_user_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `auth_user_permissions` vacia

DROP TABLE IF EXISTS `authtoken_token`;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `authtoken_token_user_id_key` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`Id_User`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `authtoken_token` (`key`, `created`, `user_id`) VALUES ('911acec5765fec4b16902779ff58480ec25eb4dc', '2026-09-07 00:32:33.167863', 1);

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_Users_Id_User` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_Users_Id_User` FOREIGN KEY (`user_id`) REFERENCES `users` (`Id_User`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `django_admin_log` vacia

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (3, 'auth', 'group');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (2, 'auth', 'permission');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (6, 'authtoken', 'token');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (7, 'authtoken', 'tokenproxy');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (5, 'sessions', 'session');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (12, 'usuarios', 'detallepedido');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (17, 'usuarios', 'miaubotaprendizaje');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (14, 'usuarios', 'miaubotconfig');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (15, 'usuarios', 'miaubotconocimiento');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (16, 'usuarios', 'miaubotfrase');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (18, 'usuarios', 'miaubotmemoriausuario');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (10, 'usuarios', 'notificacion');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (11, 'usuarios', 'pedido');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (9, 'usuarios', 'producto');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (13, 'usuarios', 'resenaproducto');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (8, 'usuarios', 'usuario');

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (1, 'contenttypes', '0001_initial', '2025-10-18 05:18:29.135828');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2025-10-18 05:18:29.359735');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (3, 'auth', '0001_initial', '2025-10-18 05:18:30.207083');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2025-10-18 05:18:30.365715');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (5, 'auth', '0003_alter_user_email_max_length', '2025-10-18 05:18:30.380365');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (6, 'auth', '0004_alter_user_username_opts', '2025-10-18 05:18:30.395252');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (7, 'auth', '0005_alter_user_last_login_null', '2025-10-18 05:18:30.412151');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (8, 'auth', '0006_require_contenttypes_0002', '2025-10-18 05:18:30.432042');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2025-10-18 05:18:30.446295');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (10, 'auth', '0008_alter_user_username_max_length', '2025-10-18 05:18:30.467878');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2025-10-18 05:18:30.481045');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (12, 'auth', '0010_alter_group_name_max_length', '2025-10-18 05:18:30.526486');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (13, 'auth', '0011_update_proxy_permissions', '2025-10-18 05:18:30.540244');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2025-10-18 05:18:30.564497');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (15, 'usuarios', '0001_initial', '2025-10-18 05:18:31.161607');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (16, 'admin', '0001_initial', '2025-10-18 05:18:31.387055');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2025-10-18 05:18:31.412247');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2025-10-18 05:18:31.440165');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (19, 'authtoken', '0001_initial', '2025-10-18 05:18:31.661300');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (20, 'authtoken', '0002_auto_20160226_1747', '2025-10-18 05:18:31.745838');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (21, 'authtoken', '0003_tokenproxy', '2025-10-18 05:18:31.761324');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (22, 'authtoken', '0004_alter_tokenproxy_options', '2025-10-18 05:18:31.775579');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (23, 'sessions', '0001_initial', '2025-10-18 05:18:31.910550');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (24, 'usuarios', '0002_producto', '2025-11-08 02:54:57.830384');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (25, 'usuarios', '0003_producto_imagen', '2025-11-08 03:06:57.064747');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (26, 'usuarios', '0004_producto_fecha_caducidad_alter_producto_precio_and_more', '2026-08-21 02:29:16.116022');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (27, 'usuarios', '0005_alter_usuario_telefono', '2026-08-21 02:29:20.575711');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (28, 'usuarios', '0006_notificacion', '2026-08-21 02:29:24.973871');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (29, 'usuarios', '0007_paymentorders_shipping_columns', '2026-08-21 02:42:19.008779');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (30, 'usuarios', '0008_orders_tables', '2026-09-07 00:01:30.441396');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (31, 'usuarios', '0009_reviews_tables', '2026-09-07 00:01:30.493749');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (32, 'usuarios', '0010_modelos_completos', '2026-09-07 00:15:46.861859');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (33, 'usuarios', '0011_usuario_username', '2026-09-07 00:31:07.516433');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (34, 'usuarios', '0012_miaubot_bd', '2026-09-07 01:11:04.053563');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (35, 'usuarios', '0013_miaubot_aprendizaje', '2026-09-07 01:15:07.650398');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (36, 'usuarios', '0014_miaubot_memoria', '2026-09-07 01:32:03.748318');

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `django_session` vacia

DROP TABLE IF EXISTS `miaubot_aprendizaje`;
CREATE TABLE `miaubot_aprendizaje` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `pregunta` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `respuesta` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `palabras_clave` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `animal` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_id` int DEFAULT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `veces_usada` int unsigned NOT NULL,
  `Fecha_Creacion` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `miaubot_aprendizaje_chk_1` CHECK ((`veces_usada` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (1, 'hola', 'Hola Admin! Me alegra verte de nuevo.\nCuéntame como esta tu mascota hoy y te ayudo con productos o consejos.', '', 'gato', 1, 'pendiente', 0, '2026-09-07 01:16:37.527213');
INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (2, 'necesito comida para perro que m e recomiendas?', 'Admin, los perros necesitan rutina: 2 comidas al dia en adultos. Elige alimento segun tamano y edad. Siempre agua fresca disponible.', 'necesito, comida, perro, recomiendas', 'perro', 1, 'pendiente', 0, '2026-09-07 01:16:46.155505');
INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (3, 'tiene 2 años y es un pitbull que me puedes dar?', 'Cuéntame mas de tu perrito: edad, tamano o que necesitas (comida, juguetes, higiene). Asi te doy una recomendacion precisa.', 'tiene, años, pitbull, puedes, dar', 'perro', 1, 'pendiente', 0, '2026-09-07 01:17:01.999870');
INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (4, 'mira es que tengo un pitbull de dos años y necestio comida para el que me puedes dar?', 'Los perros necesitan rutina: 2 comidas al dia en adultos. Elige alimento segun tamano y edad. Siempre agua fresca disponible.', 'mira, pitbull, dos, años, necestio, comida, puedes, dar', 'perro', 1, 'rechazado', 0, '2026-09-07 01:23:18.926318');
INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (5, 'que me puedes recomendar?', 'Por ahora no tengo stock para tu perrito, pero puedo darte consejos de cuidado. ¿Qué necesitas: alimentacion, juguetes o higiene?', 'puedes, recomendar', 'perro', 1, 'aprobado', 0, '2026-09-07 01:24:27.904702');
INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (6, 'tengo un pitbull de 2 anos', 'Cuéntame mas de tu pitbull: edad, tamano o que necesitas (comida, juguetes, higiene). Asi te doy una recomendacion precisa.', 'pitbull, anos', 'perro', 1, 'rechazado', 0, '2026-09-07 01:32:28.319885');
INSERT INTO `miaubot_aprendizaje` (`id`, `pregunta`, `respuesta`, `palabras_clave`, `animal`, `usuario_id`, `estado`, `veces_usada`, `Fecha_Creacion`) VALUES (7, 'necesito comida', 'Cuéntame mas de tu perrito: edad, tamaño. Asi te doy una recomendacion precisa.', 'necesito, comida', 'perro', 1, 'aprobado', 0, '2026-09-07 01:32:28.362479');

DROP TABLE IF EXISTS `miaubot_config`;
CREATE TABLE `miaubot_config` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_bot` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prompt_sistema` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje_bienvenida` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje_bienvenida_retorno` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `miaubot_config` (`id`, `nombre_bot`, `prompt_sistema`, `mensaje_bienvenida`, `mensaje_bienvenida_retorno`, `activo`, `updated_at`) VALUES (1, 'MiauBot', 'Eres MiauBot, asistente calido y experto de MiauMarket. Hablas en espanol, de forma cercana y clara. Personalizas segun el animal (gato o perro). Recomiendas SOLO productos reales del catalogo. Das consejos practicos de cuidado. Nunca inventas productos ni precios.', 'Hola! Soy MiauBot, tu asistente en MiauMarket.\nCuéntame de tu mascota (gato o perro, edad, que necesita) y te recomiendo productos reales de nuestra tienda.', 'Hola {nombre}! Me alegra verte de nuevo.\nCuéntame como esta tu mascota hoy y te ayudo con productos o consejos.', 1, '2026-09-07 01:11:03.998175');

DROP TABLE IF EXISTS `miaubot_conocimiento`;
CREATE TABLE `miaubot_conocimiento` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `animal` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tema` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `palabras_clave` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `respuesta` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `prioridad` smallint unsigned NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `miaubot_conocimiento_chk_1` CHECK ((`prioridad` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (1, 'gato', 'alimentacion', 'comida,alimento,croqueta,alimentar,taurina,comer,dieta', 'Los gatos necesitan proteina animal y taurina en su dieta. Adultos: 2 porciones al dia. Evita leche de vaca. Si tu gato es sensibil, cambia alimento gradualmente en 7 dias.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (2, 'gato', 'arena', 'arena,arenera,sanitario,orina,olor', 'Limpia desechos a diario y cambia la arena completa cada semana. Una arenera por gato mas una extra reduce accidentes fuera del arenero.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (3, 'gato', 'juguetes', 'juguete,jugar,aburrid,estimul,raton,pelota', 'Los gatos cazan por instinto. Rota juguetes cada 3-4 dias: ratones, varitas y tunel mantienen mente activa y evitan aranazos en muebles.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (4, 'gato', 'salud', 'salud,veterin,enferm,vomito,diarrea,vacuna', 'Ante vomitos repetidos, falta de apetito o letargia, consulta al veterinario. Vacunas y desparasitacion al dia protegen a largo plazo.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (5, 'gato', 'pelaje', 'pelo,pelaje,cepill,bola,bano', 'Cepilla 2-3 veces por semana. En epoca de muda, aumenta a diario para menos bolas de pelo.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (6, 'perro', 'alimentacion', 'comida,alimento,croqueta,perro,perra,cachorro,comer', 'Los perros necesitan rutina: 2 comidas al dia en adultos. Elige alimento segun tamano y edad. Siempre agua fresca disponible.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (7, 'perro', 'ejercicio', 'paseo,correr,ejercicio,energia,aburrid', 'El ejercicio diario controla peso y ansiedad. Minimo 30 min de paseo en razas medianas. Juguetes interactivos complementan en casa.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (8, 'perro', 'salud', 'salud,veterin,enferm,vacuna,garrapata,pulga', 'Revision anual, vacunas y antiparasitarios son esenciales. Revisa orejas y patas despues de cada paseo.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (9, 'general', 'compra', 'comprar,carrito,pagar,checkout,pedido', 'En Tienda agregas productos al carrito. Con sesion iniciada vas a Checkout, confirmas envio y metodo de pago. Tu pedido queda registrado al instante.', 5, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (10, 'perro', 'aprendido_7', 'necesito, comida', 'Cuéntame mas de tu perrito: edad, tamaño. Asi te doy una recomendacion precisa.', 3, 1);
INSERT INTO `miaubot_conocimiento` (`id`, `animal`, `tema`, `palabras_clave`, `respuesta`, `prioridad`, `activo`) VALUES (11, 'perro', 'aprendido_5', 'puedes, recomendar', 'Por ahora no tengo stock para tu perrito, pero puedo darte consejos de cuidado. ¿Qué necesitas: alimentacion, juguetes o higiene?', 3, 1);

DROP TABLE IF EXISTS `miaubot_frases`;
CREATE TABLE `miaubot_frases` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `animal` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `texto` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (1, 'saludo', 'gato', 'Que bueno saludarte!', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (2, 'saludo', 'gato', 'Miau! Estoy aqui para ayudarte.', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (3, 'saludo', 'perro', 'Guau! Que gusto ayudarte hoy.', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (4, 'saludo', 'general', 'Hola! Listo para ayudarte con tu mascota.', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (5, 'intro_producto', 'gato', 'Revisé el catalogo y esto le vendria genial a tu gatito:', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (6, 'intro_producto', 'gato', 'Encontre opciones que encajan con lo que buscas:', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (7, 'intro_producto', 'perro', 'Para tu perrito tengo estas opciones en stock:', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (8, 'intro_producto', 'general', 'Estas son mis mejores opciones para ti:', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (9, 'cierre_producto', 'general', 'Puedes agregarlos al carrito desde Tienda. ¿Te muestro algo mas?', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (10, 'cierre_producto', 'general', 'Si te gusta alguno, ve a Tienda y agrégalo. ¿Seguimos buscando?', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (11, 'empatia', 'gato', 'Ademas del consejo, en tienda tengo esto disponible:', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (12, 'empatia', 'perro', 'Para apoyar ese cuidado, mira estos productos:', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (13, 'despedida', 'general', 'Hasta pronto! Cuida mucho a tu mascota.', 1);
INSERT INTO `miaubot_frases` (`id`, `tipo`, `animal`, `texto`, `activo`) VALUES (14, 'despedida', 'general', 'Aqui estare cuando me necesites. Miau!', 1);

DROP TABLE IF EXISTS `miaubot_memoria`;
CREATE TABLE `miaubot_memoria` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `mascotas` json NOT NULL,
  `seguimiento` json NOT NULL,
  `mascota_activa_idx` int NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_id` (`usuario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `miaubot_memoria` (`id`, `usuario_id`, `mascotas`, `seguimiento`, `mascota_activa_idx`, `updated_at`) VALUES (2, 1, '[{"id": "7fbce458", "edad": "2 ano", "raza": "pitbull", "salud": "sano", "activa": true, "animal": "perro", "nombre": null, "tamano": "grande"}]', '{"comida": {"fecha": "2026-09-07T01:34:51.724567+00:00", "mascota_id": "7fbce458", "ultimo_mensaje": "necesito comida"}}', 0, '2026-09-07 01:34:51.727779');

DROP TABLE IF EXISTS `notificaciones`;
CREATE TABLE `notificaciones` (
  `Id_Notificacion` int NOT NULL AUTO_INCREMENT,
  `Id_User` int NOT NULL,
  `Titulo` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Mensaje` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Tipo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Id_Factura` int DEFAULT NULL,
  `Leida` tinyint(1) NOT NULL,
  `Fecha_Creacion` datetime(6) NOT NULL,
  PRIMARY KEY (`Id_Notificacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `notificaciones` vacia

DROP TABLE IF EXISTS `orders_details`;
CREATE TABLE `orders_details` (
  `Id_Detalle` int NOT NULL AUTO_INCREMENT,
  `Id_Factura` int NOT NULL,
  `Id_Products` int NOT NULL,
  `Cantidad` int NOT NULL,
  `Precio_Unitario` decimal(10,2) NOT NULL,
  `Subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`Id_Detalle`),
  KEY `fk_orders_details_factura` (`Id_Factura`),
  KEY `fk_orders_details_product` (`Id_Products`),
  CONSTRAINT `fk_orders_details_factura` FOREIGN KEY (`Id_Factura`) REFERENCES `paymentorders` (`Id_Factura`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_details_product` FOREIGN KEY (`Id_Products`) REFERENCES `products` (`Id_Products`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `orders_details` vacia

DROP TABLE IF EXISTS `paymentorders`;
CREATE TABLE `paymentorders` (
  `Id_Factura` int NOT NULL AUTO_INCREMENT,
  `Id_User` int NOT NULL,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `Total` decimal(10,2) NOT NULL,
  `Metodo_Pago` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Estado` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Pendiente',
  `Direccion_Envio` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Telefono_Envio` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`Id_Factura`),
  KEY `fk_paymentorders_user` (`Id_User`),
  CONSTRAINT `fk_paymentorders_user` FOREIGN KEY (`Id_User`) REFERENCES `users` (`Id_User`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `paymentorders` vacia

DROP TABLE IF EXISTS `product_ratings`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `product_ratings` AS select `p`.`Id_Products` AS `Id_Products`,`p`.`Titulo` AS `Titulo`,count(`r`.`Id_Review`) AS `Total_Reviews`,coalesce(avg(`r`.`Rating`),0) AS `Rating_Promedio`,coalesce(sum((case when (`r`.`Rating` = 5) then 1 else 0 end)),0) AS `Reviews_5_Estrellas`,coalesce(sum((case when (`r`.`Rating` = 4) then 1 else 0 end)),0) AS `Reviews_4_Estrellas`,coalesce(sum((case when (`r`.`Rating` = 3) then 1 else 0 end)),0) AS `Reviews_3_Estrellas`,coalesce(sum((case when (`r`.`Rating` = 2) then 1 else 0 end)),0) AS `Reviews_2_Estrellas`,coalesce(sum((case when (`r`.`Rating` = 1) then 1 else 0 end)),0) AS `Reviews_1_Estrella` from (`products` `p` left join `product_reviews` `r` on((`p`.`Id_Products` = `r`.`Id_Products`))) group by `p`.`Id_Products`,`p`.`Titulo`;

-- Tabla `product_ratings` vacia

DROP TABLE IF EXISTS `product_reviews`;
CREATE TABLE `product_reviews` (
  `Id_Review` int NOT NULL AUTO_INCREMENT,
  `Id_Products` int NOT NULL,
  `Id_User` int NOT NULL,
  `Rating` tinyint NOT NULL,
  `Comentario` text COLLATE utf8mb4_unicode_ci,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id_Review`),
  UNIQUE KEY `unique_user_product` (`Id_User`,`Id_Products`),
  KEY `idx_product_reviews` (`Id_Products`),
  KEY `idx_user_reviews` (`Id_User`),
  KEY `idx_rating` (`Rating`),
  KEY `idx_fecha` (`Fecha` DESC),
  CONSTRAINT `product_reviews_ibfk_1` FOREIGN KEY (`Id_Products`) REFERENCES `products` (`Id_Products`) ON DELETE CASCADE,
  CONSTRAINT `product_reviews_ibfk_2` FOREIGN KEY (`Id_User`) REFERENCES `users` (`Id_User`) ON DELETE CASCADE,
  CONSTRAINT `product_reviews_chk_1` CHECK (((`Rating` >= 1) and (`Rating` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `product_reviews` vacia

DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `Id_Products` int NOT NULL AUTO_INCREMENT,
  `Titulo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Descripcion` text COLLATE utf8mb4_unicode_ci,
  `Categoria` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Precio` decimal(10,2) NOT NULL,
  `Stock` int NOT NULL DEFAULT '0',
  `Imagen` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `Fecha_Caducidad` date NOT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`Id_Products`),
  KEY `created_by` (`created_by`),
  KEY `idx_products_categoria` (`Categoria`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`Id_User`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `products` vacia

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `Id_User` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Address` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `City` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `BirthDate` date NOT NULL,
  `FechaRegistro` datetime DEFAULT CURRENT_TIMESTAMP,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_staff` tinyint(1) DEFAULT '0',
  `is_superuser` tinyint(1) DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `Username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`Id_User`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Username` (`Username`),
  KEY `idx_users_email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (`Id_User`, `Nombre`, `Apellido`, `Email`, `Telefono`, `Address`, `City`, `BirthDate`, `FechaRegistro`, `password`, `is_active`, `is_staff`, `is_superuser`, `last_login`, `Username`) VALUES (1, 'Admin', 'Market', 'cadminmarket@gmail.com', '3000000000', 'Admin', 'Bogota', '1990-01-01', '2026-09-07 00:31:45', 'pbkdf2_sha256$600000$zdJbkW4443BtDgvDOtQUNt$JGQFB2uwhB59GpoIQ2S+WPIO7y7SLpms3+kHeL3Fm6M=', 1, 1, 1, NULL, 'adminmarket');

DROP TABLE IF EXISTS `users_groups`;
CREATE TABLE `users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Users_groups_usuario_id_group_id_ae446edc_uniq` (`usuario_id`,`group_id`),
  KEY `Users_groups_group_id_2ddde7ed_fk_auth_group_id` (`group_id`),
  CONSTRAINT `Users_groups_group_id_2ddde7ed_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `Users_groups_usuario_id_ca62487c_fk_Users_Id_User` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`Id_User`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `users_groups` vacia

DROP TABLE IF EXISTS `users_user_permissions`;
CREATE TABLE `users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Users_user_permissions_usuario_id_permission_id_bb90d861_uniq` (`usuario_id`,`permission_id`),
  KEY `Users_user_permissio_permission_id_7995fa19_fk_auth_perm` (`permission_id`),
  CONSTRAINT `Users_user_permissio_permission_id_7995fa19_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `Users_user_permissions_usuario_id_c50dd699_fk_Users_Id_User` FOREIGN KEY (`usuario_id`) REFERENCES `users` (`Id_User`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla `users_user_permissions` vacia

SET FOREIGN_KEY_CHECKS=1;
