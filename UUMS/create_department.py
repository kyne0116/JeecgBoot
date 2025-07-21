#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeecgBoot 部门创建工具
功能：读取Excel文件，组装JSON数据，通过API创建部门

Excel列映射：
A列 → departName (组织名称) - 必填
B列 → description (组织全称) - 必填
C列 → uumsOrgCode (组织编码) - 必填
D列 → uumsParentOrgCode (组织父编码) - 可选
E列 → orgCategory (机构类别) - 必填
"""

import requests
import json
import time
import argparse
import pandas as pd
import os
from datetime import datetime

# 配置信息
BASE_URL = "http://localhost:8080/jeecg-boot"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "123456"

REQUEST_TIMEOUT_LOGIN = 10
REQUEST_TIMEOUT_CREATE = 30
REQUEST_TIMEOUT_QUERY = 15
DISPLAY_TOKEN_LENGTH = 50


def print_excel_data(file_path):
    """打印Excel文件A-E列的内容（跳过第一行表头）"""
    try:
        print(f"📖 正在读取Excel文件: {file_path}")
        
        df = pd.read_excel(file_path, header=None)
        
        if df.empty:
            print("❌ Excel文件中没有数据")
            return None
        
        if len(df) <= 1:
            print("❌ Excel文件只有表头，没有数据行")
            return None
            
        if len(df) > 0:
            header_row = df.iloc[0]
            print(f"📋 检测到表头: {', '.join([str(header_row.iloc[i]) if pd.notna(header_row.iloc[i]) else '空' for i in range(min(5, len(header_row)))])}")
        
        data_df = df.iloc[1:].reset_index(drop=True)
        
        print(f"📊 从Excel读取到 {len(df)} 行数据（含表头），数据行: {len(data_df)} 行")
        print("\n" + "="*80)
        print("Excel文件内容 (A-E列，跳过表头):")
        print("="*80)
        
        print(f"{'行号':<4} {'A列':<20} {'B列':<25} {'C列':<15} {'D列':<15} {'E列':<10}")
        print("-" * 80)
        
        for idx, row in data_df.iterrows():
            try:
                col_a = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                col_b = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                col_c = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                col_d = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                col_e = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                
                excel_row_num = idx + 2
                print(f"{excel_row_num:<4} {col_a[:19]:<20} {col_b[:24]:<25} {col_c[:14]:<15} {col_d[:14]:<15} {col_e[:9]:<10}")
                
            except IndexError:
                excel_row_num = idx + 2
                print(f"{excel_row_num:<4} (行数据不足)")
                continue
        
        print("="*80)
        print(f"✅ 成功显示 {len(data_df)} 行数据（已跳过表头）")
        return data_df
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return None
    except Exception as e:
        print(f"❌ 读取Excel文件异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def assemble_json_data_with_parent_lookup(file_path, created_departments=None):
    """组装JSON数据并实时查询父部门：支持分批创建时的父部门查询"""
    try:
        print(f"\n🔧 开始组装JSON数据（支持实时父部门查询）...")
        
        # 读取Excel文件
        df = pd.read_excel(file_path, header=None)
        
        if df.empty:
            print("❌ Excel文件中没有数据")
            return None
        
        # 跳过第一行表头
        if len(df) <= 1:
            print("❌ Excel文件只有表头，没有数据行")
            return None
        
        # 从第二行开始处理数据
        data_df = df.iloc[1:].reset_index(drop=True)
        print(f"📊 跳过表头，开始处理 {len(data_df)} 行数据")
        
        # 获取Token用于查询父部门
        print(f"🔑 获取认证Token用于父部门查询...")
        token = get_auth_token()
        if not token:
            print("⚠️ 无法获取Token，将跳过父部门查询功能")
        
        json_data_list = []
        valid_count = 0
        error_count = 0
        parent_lookup_count = 0
        parent_found_count = 0
        
        # 遍历数据行（从第二行开始）
        for idx, row in data_df.iterrows():
            try:
                excel_row_num = idx + 2  # 实际Excel行号（从第2行开始）
                
                # 获取A-E列的值
                dept_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                description = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                uums_org_code = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                uums_parent_org_code = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                org_category = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                
                # 验证必填字段
                missing_fields = []
                if not dept_name:
                    missing_fields.append("A列(组织名称)")
                if not description:
                    missing_fields.append("B列(组织全称)")
                if not uums_org_code:
                    missing_fields.append("C列(机构编码)")
                if not org_category:
                    missing_fields.append("E列(机构类别)")
                
                if missing_fields:
                    print(f"   ⚠️ Excel第{excel_row_num}行缺少必填字段: {', '.join(missing_fields)}，跳过")
                    error_count += 1
                    continue
                
                # 组装JSON数据
                json_data = {
                    "departName": dept_name,
                    "description": description,
                    "uumsOrgCode": uums_org_code,
                    "orgCategory": org_category
                }
                
                # 可选字段：组织父编码
                if uums_parent_org_code:
                    json_data["uumsParentOrgCode"] = uums_parent_org_code
                
                # 优化：处理D列组织父编码，查询父部门并添加parentId
                if uums_parent_org_code and token:
                    print(f"   🔍 Excel第{excel_row_num}行检测到父编码: {uums_parent_org_code}，查询父部门...")
                    parent_lookup_count += 1
                    
                    # 先检查本次创建的部门中是否有匹配的父部门
                    parent_id_from_created = None
                    if created_departments:
                        for created_dept in created_departments:
                            if created_dept.get('uumsOrgCode') == uums_parent_org_code:
                                parent_id_from_created = created_dept.get('id')
                                print(f"   💡 在本次创建的部门中找到父部门ID: {parent_id_from_created}")
                                break
                    
                    if parent_id_from_created:
                        json_data["parentId"] = parent_id_from_created
                        parent_found_count += 1
                        print(f"   ✅ Excel第{excel_row_num}行使用本次创建的父部门，添加parentId: {parent_id_from_created}")
                    else:
                        # 从数据库查询父部门
                        parent_dept = query_department_by_uums_code(token, uums_parent_org_code)
                        if parent_dept and parent_dept.get('id'):
                            parent_id = parent_dept.get('id')
                            json_data["parentId"] = parent_id
                            parent_found_count += 1
                            print(f"   ✅ Excel第{excel_row_num}行在数据库中找到父部门，添加parentId: {parent_id}")
                        else:
                            print(f"   ⚠️ Excel第{excel_row_num}行未找到父部门，跳过parentId添加")
                elif uums_parent_org_code and not token:
                    print(f"   ⚠️ Excel第{excel_row_num}行有父编码但无Token，跳过父部门查询")
                
                json_data_list.append({
                    "excel_row_number": excel_row_num,  # 记录实际Excel行号
                    "data": json_data
                })
                
                valid_count += 1
                print(f"   ✅ Excel第{excel_row_num}行数据组装成功: {dept_name}")
                
            except IndexError:
                excel_row_num = idx + 2
                print(f"   ⚠️ Excel第{excel_row_num}行数据列数不足，跳过")
                error_count += 1
                continue
            except Exception as e:
                excel_row_num = idx + 2
                print(f"   ❌ Excel第{excel_row_num}行数据处理异常: {e}")
                error_count += 1
                continue
        
        print(f"\n📊 JSON数据组装完成:")
        print(f"   总行数: {len(df)} (含表头)")
        print(f"   数据行数: {len(data_df)}")
        print(f"   成功组装: {valid_count} 条")
        print(f"   跳过/错误: {error_count} 条")
        print(f"   父部门查询: {parent_lookup_count} 次")
        print(f"   找到父部门: {parent_found_count} 个")
        
        return json_data_list
        
    except Exception as e:
        print(f"❌ 组装JSON数据异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def assemble_json_data(file_path):
    """组装JSON数据：将Excel数据转换为部门创建的JSON报文格式（保持原接口兼容性）"""
    return assemble_json_data_with_parent_lookup(file_path, None)

def print_json_data(json_data_list):
    """打印组装后的JSON报文"""
    if not json_data_list:
        print("❌ 没有可打印的JSON数据")
        return
    
    print("\n" + "="*80)
    print("📋 组装后的JSON报文:")
    print("="*80)
    
    for item in json_data_list:
        excel_row_num = item['excel_row_number']
        data = item['data']
        
        print(f"\n--- Excel第{excel_row_num}行数据 ---")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print("\n" + "="*80)
    print("📋 完整JSON数组格式:")
    print("="*80)
    
    # 提取所有JSON数据
    all_json_data = [item['data'] for item in json_data_list]
    print(json.dumps(all_json_data, ensure_ascii=False, indent=2))
    
    print("="*80)
    print(f"✅ 共输出 {len(json_data_list)} 条JSON报文")

def query_department_by_uums_code(token, uums_org_code):
    """根据uumsOrgCode查询SysDepart单条记录"""
    try:
        headers = {
            'X-Access-Token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"🔍 正在查询UUMS机构编码: {uums_org_code}")
        
        # 调用JeecgBoot部门查询接口 - 获取所有部门树然后过滤
        print(f"🌐 正在调用查询API: GET {BASE_URL}/sys/sysDepart/queryTreeList")
        print(f"   查询目标: uumsOrgCode = {uums_org_code}")
        
        response = requests.get(f"{BASE_URL}/sys/sysDepart/queryTreeList", 
                              headers=headers, timeout=REQUEST_TIMEOUT_QUERY)
        
        print(f"📡 API响应状态: HTTP {response.status_code}")
        print(f"📄 响应内容: {response.text[:300]}{'...' if len(response.text) > 300 else ''}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                departments = result.get('result', [])
                if departments:
                    # 递归搜索部门树中匹配uumsOrgCode的记录
                    def find_dept_by_uums_code(dept_list, target_code):
                        for dept in dept_list:
                            if dept.get('uumsOrgCode') == target_code:
                                return dept
                            # 递归搜索子部门
                            if 'children' in dept and dept['children']:
                                found = find_dept_by_uums_code(dept['children'], target_code)
                                if found:
                                    return found
                        return None
                    
                    found_dept = find_dept_by_uums_code(departments, uums_org_code)
                    if found_dept:
                        print("✅ 查询成功，找到匹配记录")
                        print(f"📋 部门信息:")
                        print(f"   ID: {found_dept.get('id')}")
                        print(f"   部门名称: {found_dept.get('departName')}")
                        print(f"   描述: {found_dept.get('description', 'N/A')}")
                        print(f"   机构编码: {found_dept.get('orgCode')}")
                        print(f"   UUMS机构编码: {found_dept.get('uumsOrgCode')}")
                        print(f"   UUMS父机构编码: {found_dept.get('uumsParentOrgCode', 'N/A')}")
                        print(f"   机构类别: {found_dept.get('orgCategory')}")
                        print(f"   创建时间: {found_dept.get('createTime', 'N/A')}")
                        return found_dept
                    else:
                        print(f"⚠️ 未找到匹配uumsOrgCode的记录: {uums_org_code}")
                        print(f"   共搜索了 {len(departments)} 个顶级部门及其子部门")
                        return None
                else:
                    print("⚠️ 查询成功但未找到任何部门记录")
                    return None
            else:
                print(f"❌ 查询失败: {result.get('message', '未知错误')}")
                return None
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('message', response.text[:100])}"
            except:
                error_msg += f" - {response.text[:100]}"
            
            print(f"❌ 查询请求失败: {error_msg}")
            return None
            
    except Exception as e:
        print(f"❌ 查询异常: {e}")
        return None

def get_auth_token():
    """获取认证Token"""
    try:
        print(f"🔐 正在获取认证Token...")
        print(f"   服务地址: {BASE_URL}")
        print(f"   用户名: {LOGIN_USERNAME}")
        
        login_data = {"username": LOGIN_USERNAME, "password": LOGIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/sys/mLogin", json=login_data, timeout=REQUEST_TIMEOUT_LOGIN)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result['result']['token']
                print(f"✅ Token获取成功: {token[:DISPLAY_TOKEN_LENGTH]}...")
                return token
            else:
                print(f"❌ 登录失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 登录请求失败: HTTP {response.status_code}")
            print(f"   响应内容: {response.text[:200]}...")
            return None

    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def create_department_via_api(token, dept_data, excel_row_num):
    """通过API创建单个部门"""
    try:
        headers = {
            'X-Access-Token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"📋 使用第二部分组装的JSON数据 (Excel第{excel_row_num}行):")
        print(f"   部门名称: {dept_data.get('departName')}")
        print(f"   描述信息: {dept_data.get('description', 'N/A')}")
        print(f"   UUMS机构编码: {dept_data.get('uumsOrgCode', 'N/A')}")
        if 'uumsParentOrgCode' in dept_data:
            print(f"   UUMS父机构编码: {dept_data.get('uumsParentOrgCode')}")
        else:
            print(f"   UUMS父机构编码: (无)")
        if 'parentId' in dept_data:
            print(f"   父部门ID: {dept_data.get('parentId')}")
        else:
            print(f"   父部门ID: (无)")
        print(f"   机构类别: {dept_data.get('orgCategory')} (1=公司，2=组织机构，3=岗位)")
        
        # 显示完整的请求报文
        print(f"\n📄 提交的JSON请求报文:")
        print(json.dumps(dept_data, ensure_ascii=False, indent=2))
        
        # 调用JeecgBoot部门创建API
        print(f"\n🚀 正在调用API: POST {BASE_URL}/sys/sysDepart/add")
        print(f"   请求头: X-Access-Token: {token[:20]}...")
        print(f"   Content-Type: application/json")
        
        print(f"🌐 正在发送REST请求...")
        print(f"   URL: {BASE_URL}/sys/sysDepart/add")
        print(f"   Method: POST")
        print(f"   Headers: {json.dumps(headers, ensure_ascii=False, indent=4)}")
        print(f"   Body: {json.dumps(dept_data, ensure_ascii=False)}")
        
        response = requests.post(f"{BASE_URL}/sys/sysDepart/add", 
                               json=dept_data, headers=headers, timeout=REQUEST_TIMEOUT_CREATE)
        
        print(f"📡 REST请求已发送，API响应状态: HTTP {response.status_code}")
        print(f"📄 响应内容: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 部门创建成功")
                print(f"   响应消息: {result.get('message', 'N/A')}")
                return {
                    'success': True,
                    'excel_row': excel_row_num,
                    'dept_name': dept_data.get('departName'),
                    'response': result,
                    'api_message': result.get('message', 'N/A')
                }
            else:
                print(f"❌ 部门创建失败: {result.get('message', '未知错误')}")
                return {
                    'success': False,
                    'excel_row': excel_row_num,
                    'dept_name': dept_data.get('departName'),
                    'response': result,
                    'error_message': result.get('message', '未知错误')
                }
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('message', response.text[:100])}"
            except:
                error_msg += f" - {response.text[:100]}"
            
            print(f"❌ 部门创建请求失败: {error_msg}")
            return {
                'success': False,
                'excel_row': excel_row_num,
                'dept_name': dept_data.get('departName'),
                'error_message': error_msg
            }
            
    except Exception as e:
        print(f"❌ 创建部门异常: {e}")
        return {
            'success': False,
            'excel_row': excel_row_num,
            'dept_name': dept_data.get('departName', 'N/A'),
            'error_message': str(e)
        }

def create_departments_via_api_with_hierarchy(file_path):
    """智能创建部门：支持父子层级关系的正确建立"""
    print(f"\n🚀 开始智能部门创建流程（支持层级关系）...")
    
    # 1. 获取认证Token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证Token，终止创建流程")
        return None
    
    # 读取Excel数据
    df = pd.read_excel(file_path, header=None)
    if df.empty or len(df) <= 1:
        print("❌ Excel文件无有效数据")
        return None
    
    data_df = df.iloc[1:].reset_index(drop=True)
    print(f"📊 开始处理 {len(data_df)} 行数据，支持动态父部门关联")
    
    results = []
    success_count = 0
    failure_count = 0
    created_departments = []  # 记录已创建的部门信息
    
    # 逐个创建部门
    for idx, row in data_df.iterrows():
        excel_row_num = idx + 2
        
        print(f"\n📦 正在创建第 {idx+1}/{len(data_df)} 个部门 (Excel第{excel_row_num}行)...")
        print("-" * 70)
        
        try:
            # 获取当前行数据
            dept_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            description = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            uums_org_code = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
            uums_parent_org_code = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""
            org_category = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
            
            # 验证必填字段
            if not all([dept_name, description, uums_org_code, org_category]):
                print(f"❌ Excel第{excel_row_num}行数据不完整，跳过")
                results.append({
                    'success': False,
                    'excel_row': excel_row_num,
                    'dept_name': dept_name,
                    'error_message': '数据不完整'
                })
                failure_count += 1
                continue
            
            # 组装基础JSON数据
            json_data = {
                "departName": dept_name,
                "description": description,
                "uumsOrgCode": uums_org_code,
                "orgCategory": org_category
            }
            
            if uums_parent_org_code:
                json_data["uumsParentOrgCode"] = uums_parent_org_code
            
            # 智能查找父部门ID
            if uums_parent_org_code:
                print(f"🔍 查找父部门编码: {uums_parent_org_code}")
                
                # 1. 先从已创建的部门中查找
                parent_id = None
                for created_dept in created_departments:
                    if created_dept.get('uumsOrgCode') == uums_parent_org_code:
                        parent_id = created_dept.get('id')
                        print(f"💡 在本次创建的部门中找到父部门ID: {parent_id}")
                        break
                
                # 2. 如果没找到，从数据库查询
                if not parent_id:
                    parent_dept = query_department_by_uums_code(token, uums_parent_org_code)
                    if parent_dept and parent_dept.get('id'):
                        parent_id = parent_dept.get('id')
                        print(f"💡 在数据库中找到父部门ID: {parent_id}")
                
                # 3. 添加parentId到JSON数据
                if parent_id:
                    json_data["parentId"] = parent_id
                    print(f"✅ 成功添加父部门关联: parentId = {parent_id}")
                else:
                    print(f"⚠️ 未找到父部门，将作为顶级部门创建")
            
            # 创建部门
            result = create_department_via_api(token, json_data, excel_row_num)
            results.append(result)
            
            if result['success']:
                success_count += 1
                # 获取创建后的部门信息（需要查询最新创建的部门）
                print(f"🔄 查询新创建的部门信息...")
                time.sleep(2)  # 等待数据库更新
                
                new_dept = query_department_by_uums_code(token, uums_org_code)
                if new_dept:
                    created_departments.append({
                        'id': new_dept.get('id'),
                        'uumsOrgCode': uums_org_code,
                        'departName': dept_name
                    })
                    print(f"📋 记录新创建部门: {dept_name} (ID: {new_dept.get('id')})")
                else:
                    print(f"⚠️ 无法查询到新创建的部门信息")
            else:
                failure_count += 1
                print(f"❌ 部门创建失败: {result.get('error_message', '未知错误')}")
            
            # 等待间隔
            if idx < len(data_df) - 1:
                print("⏱️ 等待3秒后继续...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ 处理Excel第{excel_row_num}行时发生异常: {e}")
            results.append({
                'success': False,
                'excel_row': excel_row_num,
                'dept_name': dept_name if 'dept_name' in locals() else 'Unknown',
                'error_message': str(e)
            })
            failure_count += 1
    
    print_api_results(results, success_count, failure_count)
    
    print(f"\n📋 本次创建的部门记录:")
    for dept in created_departments:
        print(f"   {dept['departName']} (ID: {dept['id']}, 编码: {dept['uumsOrgCode']})")
    
    return results

def create_departments_via_api(json_data_list):
    """批量通过API创建部门（保持原接口兼容性）"""
    if not json_data_list:
        print("❌ 没有可创建的部门数据")
        return None
    
    print(f"\n🚀 开始通过API创建部门...")
    print(f"📊 总计需要创建 {len(json_data_list)} 个部门")
    print(f"📋 数据来源: 第二部分组装的JSON数据")
    print(f"🔗 API端点: {BASE_URL}/sys/sysDepart/add")
    print(f"🌐 即将执行 {len(json_data_list)} 次REST请求")
    print(f"⚡ REST请求方法: POST")
    print(f"🔄 执行模式: 逐个发送，间隔1秒")
    
    # 1. 获取认证Token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证Token，终止创建流程")
        return None
    
    # 2. 批量创建部门
    results = []
    success_count = 0
    failure_count = 0
    
    for i, item in enumerate(json_data_list, 1):
        excel_row_num = item['excel_row_number']
        dept_data = item['data']
        
        print(f"\n📦 正在创建第 {i}/{len(json_data_list)} 个部门...")
        print("-" * 70)
        
        result = create_department_via_api(token, dept_data, excel_row_num)
        results.append(result)
        
        if result['success']:
            success_count += 1
        else:
            failure_count += 1
        
        if i < len(json_data_list):
            print("⏱️ 等待1秒后继续...")
            time.sleep(1)
    
    print_api_results(results, success_count, failure_count)
    
    return results

def print_api_results(results, success_count, failure_count):
    """打印API调用结果"""
    print("\n" + "="*80)
    print("📊 API调用结果统计:")
    print("="*80)
    
    print(f"   总计创建: {len(results)} 个部门")
    print(f"   成功创建: {success_count} 个部门")
    print(f"   创建失败: {failure_count} 个部门")
    print(f"   成功率: {(success_count/len(results)*100):.1f}%")
    
    # 详细结果列表
    print("\n📋 详细结果列表:")
    print("-" * 80)
    print(f"{'Excel行号':<10} {'部门名称':<20} {'状态':<8} {'结果信息':<30}")
    print("-" * 80)
    
    for result in results:
        excel_row = result['excel_row']
        dept_name = result['dept_name'][:19] if len(result['dept_name']) > 19 else result['dept_name']
        status = "✅成功" if result['success'] else "❌失败"
        message = result.get('api_message', result.get('error_message', 'N/A'))[:29]
        
        print(f"{excel_row:<10} {dept_name:<20} {status:<8} {message:<30}")
    
    # 失败详情
    if failure_count > 0:
        print("\n❌ 失败详情:")
        print("-" * 80)
        for result in results:
            if not result['success']:
                excel_row = result['excel_row']
                dept_name = result['dept_name']
                error_msg = result.get('error_message', '未知错误')
                print(f"   Excel第{excel_row}行 [{dept_name}]: {error_msg}")
    
    print("="*80)


def sort_departments_by_hierarchy(file_path):
    """
    组织数据父子关系梳理：确保父节点始终出现在子节点之前
    使用拓扑排序算法处理部门层级关系
    
    Args:
        file_path (str): Excel文件路径
        
    Returns:
        bool: 排序是否成功
    """
    try:
        print("🔄 开始组织数据父子关系梳理...")
        
        # 读取Excel文件，保持原始数据格式
        df = pd.read_excel(file_path, dtype=str)
        
        # 确保有足够的列
        if df.shape[1] < 4:
            print(f"❌ 错误: Excel文件至少需要4列，当前只有{df.shape[1]}列")
            return False
        
        print(f"📊 读取到 {len(df)} 行数据（含表头）")
        
        # 获取C列和D列的值，保持原始格式
        # 检测是否有表头行
        has_header = True
        first_row = df.iloc[0] if len(df) > 0 else None
        if first_row is not None:
            # 判断第一行是否为表头（C列和D列包含非数字内容或标准表头文字）
            c_val = str(first_row.iloc[2]).strip() if pd.notna(first_row.iloc[2]) else ""
            d_val = str(first_row.iloc[3]).strip() if pd.notna(first_row.iloc[3]) else ""
            # 如果C列是纯数字，很可能不是表头
            if c_val.isdigit() or len(c_val) > 10:  # 部门编码通常较长
                has_header = False
        
        print(f"📊 检测到{'有' if has_header else '无'}表头行")
        
        # 根据是否有表头决定起始行
        start_row = 1 if has_header else 0
        data_rows = df.iloc[start_row:] if len(df) > start_row else pd.DataFrame()
        
        dept_data = []
        for i, (idx, row) in enumerate(data_rows.iterrows()):
            dept_code = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            parent_code = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
            
            # 跳过空的部门编码
            if not dept_code:
                continue
                
            dept_data.append({
                'original_index': idx,  # 原始DataFrame中的索引
                'dept_code': dept_code,
                'parent_code': parent_code if parent_code else None,
                'original_row': row
            })
        
        print(f"📋 有效部门记录: {len(dept_data)} 个")
        
        # 构建部门编码到索引的映射
        code_to_data = {item['dept_code']: item for item in dept_data}
        
        # 使用拓扑排序算法对部门进行层级排序
        def topological_sort(departments):
            """拓扑排序实现"""
            # 构建入度表和邻接表
            in_degree = {}  # 入度计数
            adj_list = {}   # 邻接表：父节点 -> [子节点列表]
            all_nodes = set()
            
            # 初始化
            for dept in departments:
                dept_code = dept['dept_code']
                parent_code = dept['parent_code']
                all_nodes.add(dept_code)
                
                if dept_code not in in_degree:
                    in_degree[dept_code] = 0
                if dept_code not in adj_list:
                    adj_list[dept_code] = []
                
                if parent_code and parent_code in code_to_data:
                    all_nodes.add(parent_code)
                    if parent_code not in in_degree:
                        in_degree[parent_code] = 0
                    if parent_code not in adj_list:
                        adj_list[parent_code] = []
                    
                    # 父节点指向子节点
                    adj_list[parent_code].append(dept_code)
                    in_degree[dept_code] += 1
            
            # 找到所有入度为0的节点（根节点）
            queue = []
            for node in all_nodes:
                if in_degree[node] == 0:
                    queue.append(node)
            
            sorted_codes = []
            
            # 拓扑排序
            while queue:
                current = queue.pop(0)
                sorted_codes.append(current)
                
                # 减少相邻节点的入度
                for neighbor in adj_list[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            # 检查是否存在环
            if len(sorted_codes) != len(all_nodes):
                remaining_nodes = all_nodes - set(sorted_codes)
                print(f"⚠️ 检测到循环依赖，涉及节点: {remaining_nodes}")
                return None
            
            return sorted_codes
        
        print("🔍 执行拓扑排序算法...")
        sorted_dept_codes = topological_sort(dept_data)
        
        if sorted_dept_codes is None:
            print("❌ 排序失败：存在循环依赖关系")
            return False
        
        print(f"✅ 拓扑排序完成，排序后顺序:")
        
        # 构建新的DataFrame，按照排序后的顺序
        sorted_rows = []
        dept_level = {}  # 记录部门层级
        processed_count = 0
        
        # 如果有表头行，首先添加表头行
        if has_header:
            sorted_rows.append(df.iloc[0])
        
        # 计算每个部门的层级
        def calculate_level(dept_code, visited=None):
            if visited is None:
                visited = set()
            
            if dept_code in visited:
                return 0  # 避免循环
            
            if dept_code in dept_level:
                return dept_level[dept_code]
            
            visited.add(dept_code)
            
            if dept_code not in code_to_data:
                level = 0
            else:
                parent_code = code_to_data[dept_code]['parent_code']
                if parent_code and parent_code in code_to_data:
                    level = calculate_level(parent_code, visited.copy()) + 1
                else:
                    level = 0
            
            dept_level[dept_code] = level
            return level
        
        # 计算所有部门的层级
        for dept_code in sorted_dept_codes:
            if dept_code in code_to_data:
                calculate_level(dept_code)
        
        # 按排序后的顺序添加行
        for dept_code in sorted_dept_codes:
            if dept_code in code_to_data:
                dept_info = code_to_data[dept_code]
                sorted_rows.append(dept_info['original_row'])
                processed_count += 1
                
                level = dept_level.get(dept_code, 0)
                parent_info = f" (父编码: {dept_info['parent_code']})" if dept_info['parent_code'] else " (根节点)"
                print(f"   第{processed_count}位: 层级{level} - {dept_code}{parent_info}")
        
        # 创建新的DataFrame
        new_df = pd.DataFrame(sorted_rows)
        
        # 保存排序后的数据到原文件
        new_df.to_excel(file_path, index=False)
        
        print(f"✅ 部门层级排序完成！")
        print(f"📊 排序统计:")
        print(f"   处理的部门: {processed_count} 个")
        print(f"   最大层级深度: {max(dept_level.values()) if dept_level else 0}")
        print(f"   根节点数量: {sum(1 for level in dept_level.values() if level == 0)}")
        print(f"📁 已保存到: {file_path}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ 错误: 文件 '{file_path}' 不存在")
        return False
    except Exception as e:
        print(f"❌ 排序处理时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def validate_department_hierarchy(file_path):
    """
    验证部门层级关系前置检查
    验证D列的值是否在C列中存在，并在F列标注Y/N
    
    Args:
        file_path (str): Excel文件路径
        
    Returns:
        bool: 验证是否成功
    """
    try:
        print("🔍 开始部门层级关系验证...")
        
        # 读取Excel文件，保持原始数据格式
        df = pd.read_excel(file_path, dtype=str)
        
        # 确保有足够的列
        if df.shape[1] < 4:
            print(f"❌ 错误: Excel文件至少需要4列，当前只有{df.shape[1]}列")
            return False
        
        # 获取C列和D列的值，保持原始格式
        c_column = df.iloc[:, 2].dropna().astype(str).str.strip()
        d_column = df.iloc[:, 3].fillna('').astype(str).str.strip()
        
        print(f"📊 检测到 {len(c_column)} 个C列编码值")
        print(f"📊 检测到 {len(d_column)} 个D列父编码值")
        
        # 创建C列值的集合用于快速查找
        c_values_set = set(c_column.tolist())
        print(f"🔍 C列唯一值集合: {len(c_values_set)} 个")
        
        # 验证D列的值是否在C列中存在
        validation_results = []
        valid_parent_count = 0
        invalid_parent_count = 0
        empty_parent_count = 0
        
        for i, d_value in enumerate(d_column):
            if d_value == '' or pd.isna(d_value):
                validation_results.append('N')
                empty_parent_count += 1
            else:
                if d_value in c_values_set:
                    validation_results.append('Y')
                    valid_parent_count += 1
                else:
                    validation_results.append('N')
                    invalid_parent_count += 1
                    print(f"⚠️ 第{i+2}行: D列父编码 '{d_value}' 在C列中未找到")
        
        # 在右侧新增一列（组织检查情况）
        df['组织检查情况'] = validation_results
        
        # 直接保存回原文件
        df.to_excel(file_path, index=False)
        
        print(f"✅ 验证完成！组织检查情况列已添加到: {file_path}")
        
        # 输出统计信息
        print(f"📊 验证统计:")
        print(f"   有效父编码: {valid_parent_count} 个 (Y)")
        print(f"   无效父编码: {invalid_parent_count} 个 (N)")
        print(f"   空父编码: {empty_parent_count} 个 (N)")
        print(f"   总计: {len(validation_results)} 行")
        
        # 判断是否可以继续创建部门
        if invalid_parent_count > 0:
            print(f"⚠️ 发现 {invalid_parent_count} 个无效的父编码引用")
            print("💡 建议修正Excel文件中的D列父编码后再继续创建部门")
            return False
        else:
            print("✅ 所有父编码引用都有效，可以继续创建部门")
            return True
        
    except FileNotFoundError:
        print(f"❌ 错误: 文件 '{file_path}' 不存在")
        return False
    except Exception as e:
        print(f"❌ 处理文件时发生错误: {str(e)}")
        return False


def clean_test_data(file_path):
    """清理测试数据：删除Excel中指定的所有部门记录"""
    print("🧹 开始清理测试数据...")
    
    # 获取Token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取Token，清理终止")
        return
    
    # 读取Excel文件获取要删除的部门编码
    try:
        df = pd.read_excel(file_path, header=None)
        if df.empty or len(df) <= 1:
            print("❌ Excel文件无有效数据")
            return
        
        data_df = df.iloc[1:].reset_index(drop=True)
        uums_codes_to_delete = []
        
        for idx, row in data_df.iterrows():
            uums_org_code = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
            if uums_org_code:
                uums_codes_to_delete.append(uums_org_code)
        
        print(f"📋 准备删除 {len(uums_codes_to_delete)} 个部门:")
        for code in uums_codes_to_delete:
            print(f"   - {code}")
        
        deleted_count = 0
        not_found_count = 0
        
        for uums_code in uums_codes_to_delete:
            print(f"\n🔍 查找部门: {uums_code}")
            dept = query_department_by_uums_code(token, uums_code)
            
            if dept and dept.get('id'):
                dept_id = dept.get('id')
                dept_name = dept.get('departName', 'Unknown')
                print(f"🗑️ 删除部门: {dept_name} (ID: {dept_id})")
                
                try:
                    headers = {
                        'X-Access-Token': token,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                    
                    response = requests.delete(f"{BASE_URL}/sys/sysDepart/delete?id={dept_id}", 
                                             headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            print(f"✅ 删除成功: {dept_name}")
                            deleted_count += 1
                        else:
                            print(f"❌ 删除失败: {result.get('message', '未知错误')}")
                    else:
                        print(f"❌ 删除请求失败: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ 删除异常: {e}")
            else:
                print(f"⚠️ 部门不存在，跳过")
                not_found_count += 1
            
            time.sleep(1)  # 等待间隔
        
        print(f"\n📊 清理完成:")
        print(f"   成功删除: {deleted_count} 个部门")
        print(f"   未找到: {not_found_count} 个部门")
        
    except Exception as e:
        print(f"❌ 清理异常: {e}")

def test_query_function():
    """测试查询功能"""
    print("🧪 开始测试查询功能")
    print("=" * 60)
    
    # 获取Token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取Token，测试终止")
        return
    
    # 测试查询
    test_uums_code = "4772338661636601428"
    print(f"\n🔍 测试查询UUMS机构编码: {test_uums_code}")
    print("-" * 60)
    
    result = query_department_by_uums_code(token, test_uums_code)
    
    if result:
        print(f"\n✅ 测试成功，查询到部门记录")
    else:
        print(f"\n⚠️ 测试完成，未查询到匹配记录")
    
    print("=" * 60)
    print("🧪 查询功能测试完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='JeecgBoot部门创建工具 - Excel数据处理和API创建')
    parser.add_argument('--file', '-f', type=str, default='组织信息导入.xlsx',
                       help='Excel文件路径（默认: 组织信息导入.xlsx）')
    parser.add_argument('--test-query', action='store_true',
                       help='测试查询功能（使用测试参数4772338661636601428）')
    parser.add_argument('--clean-test-data', action='store_true',
                       help='清理测试数据（删除Excel中的所有部门记录）')
    parser.add_argument('--validate-only', action='store_true',
                       help='仅执行部门层级关系验证，不创建部门')
    parser.add_argument('--sort-only', action='store_true',
                       help='仅执行组织数据父子关系梳理排序，不创建部门')
    
    args = parser.parse_args()
    
    # 如果是测试查询功能
    if args.test_query:
        test_query_function()
        return
    
    # 如果是清理测试数据
    if args.clean_test_data:
        clean_test_data(args.file)
        return
    
    # 如果仅执行验证
    if args.validate_only:
        print("🔍 仅执行部门层级关系验证模式")
        print("=" * 70)
        validate_department_hierarchy(args.file)
        return
    
    # 如果仅执行排序
    if args.sort_only:
        print("🔄 仅执行组织数据父子关系梳理模式")
        print("=" * 70)
        sort_departments_by_hierarchy(args.file)
        return
    
    print("🏢 JeecgBoot部门创建工具")
    print("=" * 70)
    print(f"🕐 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Excel文件: {args.file}")
    print(f"🔗 服务地址: {BASE_URL}")
    print("📋 列说明:")
    print("   A列 → 组织名称 (departName) - 必填")
    print("   B列 → 组织全称 (description) - 必填") 
    print("   C列 → 组织编码 (uumsOrgCode) - 必填")
    print("   D列 → 组织父编码 (uumsParentOrgCode) - 可选")
    print("   E列 → 机构类别 (orgCategory) - 必填")
    print("\n🔧 功能说明:")
    print("   0️⃣ 部门层级关系前置验证（验证D列父编码是否在C列中存在）")
    print("   0️⃣.1 组织数据父子关系梳理（使用拓扑排序确保父节点在子节点之前）")
    print("   1️⃣ 显示Excel原始数据")
    print("   2️⃣ 组装JSON报文数据")
    print("   3️⃣ 通过API创建部门")
    print("       🌐 将向后端发送真实的HTTP POST请求")
    print("       📡 API端点: POST /sys/sysDepart/add")
    print("\n💡 其他功能:")
    print("   🔍 查询测试: python3 create_department.py --test-query")
    print("   🧹 清理数据: python3 create_department.py --clean-test-data")
    print("   ✅ 仅验证层级: python3 create_department.py --validate-only")
    print("   🔄 仅排序数据: python3 create_department.py --sort-only")
    
    if not os.path.exists(args.file):
        print(f"❌ Excel文件不存在: {args.file}")
        return
    
    file_ext = os.path.splitext(args.file)[1].lower()
    if file_ext not in ['.xlsx', '.xls']:
        print(f"❌ 不支持的文件格式: {file_ext}，请使用Excel文件(.xlsx, .xls)")
        return
    
    print(f"\n" + "="*70)
    print("0️⃣ 部门层级关系前置验证:")
    print("="*70)
    
    # 执行前置验证
    validation_success = validate_department_hierarchy(args.file)
    if not validation_success:
        print("❌ 验证失败，无法继续创建部门")
        print("💡 请修正Excel文件中的D列父编码后重试")
        return
    
    print(f"\n" + "="*70)
    print("0️⃣.1 组织数据父子关系梳理:")
    print("="*70)
    
    # 执行父子关系排序
    sort_success = sort_departments_by_hierarchy(args.file)
    if not sort_success:
        print("❌ 排序失败，无法继续创建部门")
        print("💡 请检查Excel文件中是否存在循环依赖关系")
        return
    
    print(f"\n" + "="*70)
    print("1️⃣ Excel原始数据展示:")
    print("="*70)
    df = print_excel_data(args.file)
    
    if df is not None:
        print(f"\n" + "="*70)
        print("2️⃣ JSON报文组装:")
        print("="*70)
        json_data_list = assemble_json_data(args.file)
        
        if json_data_list:
            print_json_data(json_data_list)
            
            print(f"\n" + "="*70)
            print("3️⃣ 通过API创建部门:")
            print("="*70)
            
            print(f"🚀 开始智能部门创建流程")
            print(f"   服务地址: {BASE_URL}")
            print(f"   用户名: {LOGIN_USERNAME}")
            print(f"   创建模式: 支持父子层级关系的智能创建")
            print(f"   提交方式: 逐个调用 POST /sys/sysDepart/add")
            print(f"   特色功能: 自动识别并建立父部门关联")
            
            print(f"✅ 开始智能创建流程（自动处理parentId）...")
            api_results = create_departments_via_api_with_hierarchy(args.file)
            if api_results:
                print("✅ 智能部门创建流程完成")
            else:
                print("❌ 智能部门创建流程失败")
        else:
            print("❌ JSON数据组装失败，无法进行API创建")
    
    print(f"\n✅ 程序执行完成")

if __name__ == "__main__":
    main()