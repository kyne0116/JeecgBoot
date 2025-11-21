-- 注意：该页面对应的前台目录为views/uums文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值


INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external) 
VALUES ('2025081310242260430', '1439398677984878593', '主数据用户变更日志', '/uums/uumsChangeUserLogList', 'uums/UumsChangeUserLogList', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0);

-- 权限控制sql
-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('2025081310242270431', '2025081310242260430', '添加主数据用户变更日志', NULL, NULL, 0, NULL, NULL, 2, 'uums:us_log_uums_change_user:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0, 0, '1', 0);
-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('2025081310242270432', '2025081310242260430', '编辑主数据用户变更日志', NULL, NULL, 0, NULL, NULL, 2, 'uums:us_log_uums_change_user:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0, 0, '1', 0);
-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('2025081310242270433', '2025081310242260430', '删除主数据用户变更日志', NULL, NULL, 0, NULL, NULL, 2, 'uums:us_log_uums_change_user:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0, 0, '1', 0);
-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('2025081310242270434', '2025081310242260430', '批量删除主数据用户变更日志', NULL, NULL, 0, NULL, NULL, 2, 'uums:us_log_uums_change_user:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0, 0, '1', 0);
-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('2025081310242270435', '2025081310242260430', '导出excel_主数据用户变更日志', NULL, NULL, 0, NULL, NULL, 2, 'uums:us_log_uums_change_user:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0, 0, '1', 0);
-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('2025081310242270436', '2025081310242260430', '导入excel_主数据用户变更日志', NULL, NULL, 0, NULL, NULL, 2, 'uums:us_log_uums_change_user:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-08-13 22:24:43', NULL, NULL, 0, 0, '1', 0);