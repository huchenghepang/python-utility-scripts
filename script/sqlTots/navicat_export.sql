/*
 Navicat Premium Dump SQL

 Source Server         : 本机的docker上的mysql
 Source Server Type    : MySQL
 Source Server Version : 80025 (8.0.25)
 Source Host           : localhost:3306
 Source Schema         : my_store

 Target Server Type    : MySQL
 Target Server Version : 80025 (8.0.25)
 File Encoding         : 65001

 Date: 08/01/2025 22:22:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for Permissions
-- ----------------------------
DROP TABLE IF EXISTS `Permissions`;
CREATE TABLE `Permissions`  (
  `permission_id` int NOT NULL AUTO_INCREMENT,
  `permission_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `type` enum('route','button') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parent_id` int NULL DEFAULT NULL,
  `can_delete` tinyint(1) NULL DEFAULT 1,
  `permission_value` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`permission_id`) USING BTREE,
  UNIQUE INDEX `permission_name`(`permission_name` ASC) USING BTREE,
  INDEX `parent_id`(`parent_id` ASC) USING BTREE,
  CONSTRAINT `Permissions_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `Permissions` (`permission_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 104 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for RolePermissions
-- ----------------------------
DROP TABLE IF EXISTS `RolePermissions`;
CREATE TABLE `RolePermissions`  (
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `permission_id`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `RolePermissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `Roles` (`role_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `RolePermissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `Permissions` (`permission_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for Roles
-- ----------------------------
DROP TABLE IF EXISTS `Roles`;
CREATE TABLE `Roles`  (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL COMMENT '自动得到创建的时间',
  `updated_at` timestamp NULL DEFAULT NULL COMMENT '更新时得到时间',
  PRIMARY KEY (`role_id`) USING BTREE,
  UNIQUE INDEX `role_name`(`role_name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 52 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for UserRoles
-- ----------------------------
DROP TABLE IF EXISTS `UserRoles`;
CREATE TABLE `UserRoles`  (
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `UserRoles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `UserRoles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `Roles` (`role_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for article_categories
-- ----------------------------
DROP TABLE IF EXISTS `article_categories`;
CREATE TABLE `article_categories`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parent_id` int NULL DEFAULT NULL,
  `level` tinyint NOT NULL,
  `slug` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`, `name`) USING BTREE,
  UNIQUE INDEX `cayegories_name`(`name` ASC) USING BTREE COMMENT '唯一',
  INDEX `id`(`id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 53 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for comment_likes
-- ----------------------------
DROP TABLE IF EXISTS `comment_likes`;
CREATE TABLE `comment_likes`  (
  `like_id` int NOT NULL AUTO_INCREMENT,
  `user_id` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `comment_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`like_id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC, `comment_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 292 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for comments
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments`  (
  `comment_id` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `article_id` int NOT NULL,
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parent_id` int UNSIGNED NULL DEFAULT 0,
  `content` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `status` enum('pending','approved','rejected') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'pending',
  `like_count` int UNSIGNED NULL DEFAULT 0,
  `reply_count` int UNSIGNED NULL DEFAULT 0,
  PRIMARY KEY (`comment_id`, `article_id`, `user_id`) USING BTREE,
  INDEX `article_id`(`article_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `comment_id`(`comment_id` ASC) USING BTREE,
  CONSTRAINT `article_id` FOREIGN KEY (`article_id`) REFERENCES `notes` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 129 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for files_info
-- ----------------------------
DROP TABLE IF EXISTS `files_info`;
CREATE TABLE `files_info`  (
  `file_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT '文件名',
  `file_id` int NOT NULL AUTO_INCREMENT COMMENT '文件id',
  `file_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件路径',
  `file_ext` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件后缀',
  `upload_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '文件上传时间',
  `file_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件的类型（MIME类型）',
  `file_size` bigint NOT NULL COMMENT '文件的大小',
  `file_fullname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件全名',
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户id',
  `hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件的哈希值',
  `status` enum('active','inactive','deleted') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文件的状态',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '文件的描述',
  PRIMARY KEY (`file_id` DESC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for note_tags
-- ----------------------------
DROP TABLE IF EXISTS `note_tags`;
CREATE TABLE `note_tags`  (
  `note_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`note_id`, `tag_id`) USING BTREE,
  INDEX `tag_id`(`tag_id` ASC) USING BTREE,
  CONSTRAINT `note_tags_ibfk_1` FOREIGN KEY (`note_id`) REFERENCES `notes` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `note_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for notes
-- ----------------------------
DROP TABLE IF EXISTS `notes`;
CREATE TABLE `notes`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `category_id` int NOT NULL,
  `file_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `create_time` datetime NOT NULL,
  `is_archive` tinyint(1) NOT NULL DEFAULT 0,
  `summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '文档的摘要',
  `toc` json NULL COMMENT '文档的目录',
  `reading` int(6) UNSIGNED ZEROFILL NOT NULL DEFAULT 000000,
  `updated_time` datetime NULL DEFAULT NULL,
  `comment_count` int(10) UNSIGNED ZEROFILL NOT NULL DEFAULT 0000000000,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `file_id`(`file_id` ASC) USING BTREE,
  INDEX `category_id`(`category_id` ASC) USING BTREE,
  INDEX `id`(`id` ASC) USING BTREE,
  CONSTRAINT `category_id` FOREIGN KEY (`category_id`) REFERENCES `article_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `n_and_f_file_id` FOREIGN KEY (`file_id`) REFERENCES `files_info` (`file_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 151 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for sessions
-- ----------------------------
DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions`  (
  `session_id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `expires` int UNSIGNED NOT NULL,
  `data` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  PRIMARY KEY (`session_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for tags
-- ----------------------------
DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id` DESC) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 187 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_comments
-- ----------------------------
DROP TABLE IF EXISTS `user_comments`;
CREATE TABLE `user_comments`  (
  `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `comment_id` int UNSIGNED NOT NULL,
  `liked` enum('false','true') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'false',
  `report` enum('true','false') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'false',
  `commented` enum('true','false') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id` DESC, `user_id`, `comment_id`) USING BTREE,
  INDEX `user_comment_user_id`(`user_id` ASC) USING BTREE,
  INDEX `user_comment_id`(`comment_id` ASC) USING BTREE,
  CONSTRAINT `user_comment_id` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`comment_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_comment_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_info
-- ----------------------------
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info`  (
  `index` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '序号',
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '用户ID',
  `account` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '账号',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码\r\n',
  `register_datetime` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `is_login` tinyint NOT NULL DEFAULT 0 COMMENT '是否登录',
  `is_delete` tinyint NOT NULL DEFAULT 0 COMMENT '是否注销了账号',
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '未知' COMMENT '用户别名',
  `role` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户角色\r\n',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的头像',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的邮箱',
  `signature` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的个性签名',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `index`(`index` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- View structure for category_note_count
-- ----------------------------
DROP VIEW IF EXISTS `category_note_count`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `category_note_count` AS select `ac`.`name` AS `category_name`,count(`n`.`id`) AS `note_count`,sum(`n`.`reading`) AS `reading`,`ac`.`level` AS `level` from (`article_categories` `ac` left join `notes` `n` on((`ac`.`id` = `n`.`category_id`))) group by `ac`.`name` order by `note_count` desc;

-- ----------------------------
-- View structure for notes_statistics
-- ----------------------------
DROP VIEW IF EXISTS `notes_statistics`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `notes_statistics` AS select `notes`.`name` AS `name`,`notes`.`file_id` AS `fileID`,`notes`.`reading` AS `reading` from `notes` where (`notes`.`is_archive` = 1);

-- ----------------------------
-- View structure for tag_note_count
-- ----------------------------
DROP VIEW IF EXISTS `tag_note_count`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `tag_note_count` AS select `t`.`name` AS `tag_name`,count(`nt`.`note_id`) AS `note_count` from (`tags` `t` join `note_tags` `nt` on((`t`.`id` = `nt`.`tag_id`))) group by `t`.`name` order by `note_count` desc;

-- ----------------------------
-- Procedure structure for addNoteWithInfo
-- ----------------------------
DROP PROCEDURE IF EXISTS `addNoteWithInfo`;
delimiter ;;
CREATE PROCEDURE `addNoteWithInfo`()

;;
delimiter ;

-- ----------------------------
-- Function structure for getAllNotesWithByCondition
-- ----------------------------
DROP FUNCTION IF EXISTS `getAllNotesWithByCondition`;
delimiter ;;
CREATE FUNCTION `getAllNotesWithByCondition`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Function structure for getAllNotesWithTags_JSON
-- ----------------------------
DROP FUNCTION IF EXISTS `getAllNotesWithTags_JSON`;
delimiter ;;
CREATE FUNCTION `getAllNotesWithTags_JSON`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Procedure structure for getNoteCounts_JSON
-- ----------------------------
DROP PROCEDURE IF EXISTS `getNoteCounts_JSON`;
delimiter ;;
CREATE PROCEDURE `getNoteCounts_JSON`()
  READS SQL DATA

;;
delimiter ;

-- ----------------------------
-- Function structure for getNotesWithTagsByCategory_JSON
-- ----------------------------
DROP FUNCTION IF EXISTS `getNotesWithTagsByCategory_JSON`;
delimiter ;;
CREATE FUNCTION `getNotesWithTagsByCategory_JSON`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Function structure for getNotesWithTagsByDateRange_JSON
-- ----------------------------
DROP FUNCTION IF EXISTS `getNotesWithTagsByDateRange_JSON`;
delimiter ;;
CREATE FUNCTION `getNotesWithTagsByDateRange_JSON`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Function structure for getNotesWithTagsByName_JSON
-- ----------------------------
DROP FUNCTION IF EXISTS `getNotesWithTagsByName_JSON`;
delimiter ;;
CREATE FUNCTION `getNotesWithTagsByName_JSON`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Function structure for getNotesWithTagsByTag_JSON
-- ----------------------------
DROP FUNCTION IF EXISTS `getNotesWithTagsByTag_JSON`;
delimiter ;;
CREATE FUNCTION `getNotesWithTagsByTag_JSON`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Function structure for getNotesWithTags_JSON
-- ----------------------------
DROP FUNCTION IF EXISTS `getNotesWithTags_JSON`;
delimiter ;;
CREATE FUNCTION `getNotesWithTags_JSON`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Function structure for getNotesWithTags_JSONByPageLimit
-- ----------------------------
DROP FUNCTION IF EXISTS `getNotesWithTags_JSONByPageLimit`;
delimiter ;;
CREATE FUNCTION `getNotesWithTags_JSONByPageLimit`()
  READS SQL DATA
  DETERMINISTIC

;;
delimiter ;

-- ----------------------------
-- Triggers structure for table Roles
-- ----------------------------
DROP TRIGGER IF EXISTS `before_insert_roles`;
delimiter ;;
CREATE TRIGGER `before_insert_roles` BEFORE INSERT ON `Roles` FOR EACH ROW SET NEW.created_at = NOW(), NEW.updated_at = NOW()
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table Roles
-- ----------------------------
DROP TRIGGER IF EXISTS `before_update_roles`;
delimiter ;;
CREATE TRIGGER `before_update_roles` BEFORE UPDATE ON `Roles` FOR EACH ROW SET NEW.updated_at = NOW()
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table comments
-- ----------------------------
DROP TRIGGER IF EXISTS `update_comment_datetime`;
delimiter ;;
CREATE TRIGGER `update_comment_datetime` BEFORE UPDATE ON `comments` FOR EACH ROW IF OLD.content <> NEW.content THEN
    SET NEW.updated_at = NOW();
ELSE
    -- 如果仅更新其他字段（如状态），不更新 updated_at
    SET NEW.updated_at = OLD.updated_at;  -- 保持原来的时间戳
END IF
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table comments
-- ----------------------------
DROP TRIGGER IF EXISTS `create_comment_datetime`;
delimiter ;;
CREATE TRIGGER `create_comment_datetime` BEFORE INSERT ON `comments` FOR EACH ROW SET NEW.created_at = NOW(),NEW.updated_at = NOW()
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table comments
-- ----------------------------
DROP TRIGGER IF EXISTS `update_comment_count_on_delete`;
delimiter ;;
CREATE TRIGGER `update_comment_count_on_delete` AFTER DELETE ON `comments` FOR EACH ROW BEGIN
    -- 删除评论时，减少 notes 表中的 comment_count
    UPDATE notes
    SET comment_count = CASE
        WHEN comment_count > 0 THEN comment_count - 1
        ELSE 0
    END
    WHERE id = OLD.article_id;  -- 使用 OLD.article_id 确保删除的是原来关联的 article
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table comments
-- ----------------------------
DROP TRIGGER IF EXISTS `update_comment_count`;
delimiter ;;
CREATE TRIGGER `update_comment_count` AFTER UPDATE ON `comments` FOR EACH ROW BEGIN
    -- 当 status 从非 approved 变为 approved
    IF OLD.status != 'approved' AND NEW.status = 'approved' THEN
        -- 增加 notes 表中的 comment_count
        UPDATE notes
        SET comment_count = comment_count + 1
        WHERE id = NEW.article_id;  -- 假设 comments 表中的 article_id 关联到 notes 表的 id
    -- 当 status 从 approved 变为其他状态
    ELSEIF OLD.status = 'approved' AND NEW.status != 'approved' THEN
        -- 减少 notes 表中的 comment_count，但不能减少到负数
        UPDATE notes
        SET comment_count = CASE
            WHEN comment_count > 0 THEN comment_count - 1
            ELSE 0
        END
        WHERE id = OLD.article_id;  -- 使用 OLD.article_id 确保删除的是原来关联的 article
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table notes
-- ----------------------------
DROP TRIGGER IF EXISTS `before_insert_note`;
delimiter ;;
CREATE TRIGGER `before_insert_note` BEFORE INSERT ON `notes` FOR EACH ROW SET NEW.updated_time = NOW()
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table notes
-- ----------------------------
DROP TRIGGER IF EXISTS `before_update_note`;
delimiter ;;
CREATE TRIGGER `before_update_note` BEFORE UPDATE ON `notes` FOR EACH ROW IF OLD.file_id<>NEW.file_id THEN
  SET NEW.updated_time = NOW();
END IF
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table user_info
-- ----------------------------
DROP TRIGGER IF EXISTS `assignuserrole`;
delimiter ;;
CREATE TRIGGER `assignuserrole` AFTER INSERT ON `user_info` FOR EACH ROW BEGIN
INSERT INTO UserRoles (user_id, role_id) VALUES (NEW.user_id, 39);
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
