-- 自动化工厂数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS auto_factory DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，如需要）
-- CREATE USER 'auto_factory'@'%' IDENTIFIED BY 'auto_factory_123';
-- GRANT ALL PRIVILEGES ON auto_factory.* TO 'auto_factory'@'%';
-- FLUSH PRIVILEGES;

SELECT '数据库创建成功！' as message;
