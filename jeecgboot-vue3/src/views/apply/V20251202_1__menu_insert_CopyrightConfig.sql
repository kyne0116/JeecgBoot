-- 注意：该页面对应的前台目录为views/apply文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值


-- 主菜单
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('176466423761901', NULL, '软著申请配置表', '/apply/copyrightConfigList', 'apply/CopyrightConfigList', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0);

-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466423761902', '176466423761901', '添加软著申请配置表', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightconfig:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0, 0, '1', 0);

-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466423761903', '176466423761901', '编辑软著申请配置表', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightconfig:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0, 0, '1', 0);

-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466423761904', '176466423761901', '删除软著申请配置表', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightconfig:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0, 0, '1', 0);

-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466423761905', '176466423761901', '批量删除软著申请配置表', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightconfig:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0, 0, '1', 0);

-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466423761906', '176466423761901', '导出excel_软著申请配置表', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightconfig:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0, 0, '1', 0);

-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466423761907', '176466423761901', '导入excel_软著申请配置表', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightconfig:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 16:30:37', NULL, NULL, 0, 0, '1', 0);

-- 角色授权（以 admin 角色为例，role_id 可替换）
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761908', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761901', NULL, '2025-12-02 16:30:37', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761909', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761902', NULL, '2025-12-02 16:30:37', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761910', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761903', NULL, '2025-12-02 16:30:37', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761911', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761904', NULL, '2025-12-02 16:30:37', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761912', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761905', NULL, '2025-12-02 16:30:37', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761913', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761906', NULL, '2025-12-02 16:30:37', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466423761914', 'f6817f48af4fb3af11b9e8bf182f618b', '176466423761907', NULL, '2025-12-02 16:30:37', '127.0.0.1');