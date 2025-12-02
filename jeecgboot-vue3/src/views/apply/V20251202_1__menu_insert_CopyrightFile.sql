-- 注意：该页面对应的前台目录为views/apply文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值


-- 主菜单
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('176466313495501', NULL, '软著文件记录', '/apply/copyrightFileList', 'apply/CopyrightFileList', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0);

-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466313495502', '176466313495501', '添加软著文件记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightfile:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0, 0, '1', 0);

-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466313495503', '176466313495501', '编辑软著文件记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightfile:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0, 0, '1', 0);

-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466313495504', '176466313495501', '删除软著文件记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightfile:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0, 0, '1', 0);

-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466313495505', '176466313495501', '批量删除软著文件记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightfile:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0, 0, '1', 0);

-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466313495506', '176466313495501', '导出excel_软著文件记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightfile:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0, 0, '1', 0);

-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466313495507', '176466313495501', '导入excel_软著文件记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightfile:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:12:14', NULL, NULL, 0, 0, '1', 0);

-- 角色授权（以 admin 角色为例，role_id 可替换）
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495508', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495501', NULL, '2025-12-02 16:12:14', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495509', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495502', NULL, '2025-12-02 16:12:14', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495510', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495503', NULL, '2025-12-02 16:12:14', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495511', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495504', NULL, '2025-12-02 16:12:14', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495512', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495505', NULL, '2025-12-02 16:12:14', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495513', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495506', NULL, '2025-12-02 16:12:14', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466313495514', 'f6817f48af4fb3af11b9e8bf182f618b', '176466313495507', NULL, '2025-12-02 16:12:14', '127.0.0.1');