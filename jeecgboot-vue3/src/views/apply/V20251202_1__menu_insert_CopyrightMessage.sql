-- 注意：该页面对应的前台目录为views/apply文件夹下
-- 如果你想更改到其他目录，请修改sql中component字段对应的值


-- 主菜单
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('176466201826701', NULL, '软著申请聊天记录', '/apply/copyrightMessageList', 'apply/CopyrightMessageList', NULL, NULL, 0, NULL, '1', 0.00, 0, NULL, 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0);

-- 新增
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466201826702', '176466201826701', '添加软著申请聊天记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightmessage:add', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0, 0, '1', 0);

-- 编辑
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466201826703', '176466201826701', '编辑软著申请聊天记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightmessage:edit', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0, 0, '1', 0);

-- 删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466201826704', '176466201826701', '删除软著申请聊天记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightmessage:delete', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0, 0, '1', 0);

-- 批量删除
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466201826705', '176466201826701', '批量删除软著申请聊天记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightmessage:deleteBatch', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0, 0, '1', 0);

-- 导出excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466201826706', '176466201826701', '导出excel_软著申请聊天记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightmessage:exportXls', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0, 0, '1', 0);

-- 导入excel
INSERT INTO sys_permission(id, parent_id, name, url, component, is_route, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_leaf, keep_alive, hidden, hide_tab, description, create_by, create_time, update_by, update_time, del_flag, rule_flag, status, internal_or_external)
VALUES ('176466201826707', '176466201826701', '导入excel_软著申请聊天记录', NULL, NULL, 0, NULL, NULL, 2, 'apply:copyright_apply_copyrightmessage:importExcel', '1', NULL, 0, NULL, 1, 0, 0, 0, NULL, 'admin', '2025-12-02 15:53:38', NULL, NULL, 0, 0, '1', 0);

-- 角色授权（以 admin 角色为例，role_id 可替换）
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826708', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826701', NULL, '2025-12-02 15:53:38', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826709', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826702', NULL, '2025-12-02 15:53:38', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826710', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826703', NULL, '2025-12-02 15:53:38', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826711', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826704', NULL, '2025-12-02 15:53:38', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826712', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826705', NULL, '2025-12-02 15:53:38', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826713', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826706', NULL, '2025-12-02 15:53:38', '127.0.0.1');
INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip) VALUES ('176466201826714', 'f6817f48af4fb3af11b9e8bf182f618b', '176466201826707', NULL, '2025-12-02 15:53:38', '127.0.0.1');