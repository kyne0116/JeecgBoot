-- 注意：该页面对应的前台目录为views/apply文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值


-- 主菜单
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('176464987892001', NULL, '软著申请申请会话', '/apply/copyrightSessionList', 'apply/CopyrightSessionList', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0);

-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176464987892002', '176464987892001', '添加软著申请申请会话', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightsession:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0, 0, '1', 0);

-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176464987892003', '176464987892001', '编辑软著申请申请会话', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightsession:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0, 0, '1', 0);

-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176464987892004', '176464987892001', '删除软著申请申请会话', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightsession:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0, 0, '1', 0);

-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176464987892005', '176464987892001', '批量删除软著申请申请会话', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightsession:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0, 0, '1', 0);

-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176464987892006', '176464987892001', '导出excel_软著申请申请会话', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightsession:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0, 0, '1', 0);

-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176464987892007', '176464987892001', '导入excel_软著申请申请会话', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightsession:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 12:31:18', NULL, NULL, 0, 0, '1', 0);

-- 角色授权（以 admin 角色为例，role_id 可替换）
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892008', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892001', NULL, '2025-12-02 12:31:18', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892009', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892002', NULL, '2025-12-02 12:31:18', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892010', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892003', NULL, '2025-12-02 12:31:18', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892011', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892004', NULL, '2025-12-02 12:31:18', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892012', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892005', NULL, '2025-12-02 12:31:18', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892013', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892006', NULL, '2025-12-02 12:31:18', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176464987892014', 'f6817f48af4fb3af11b9e8bf182f618b', '176464987892007', NULL, '2025-12-02 12:31:18', '127.0.0.1');