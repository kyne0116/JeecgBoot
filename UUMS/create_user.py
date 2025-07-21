#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人员信息处理脚本
功能：
1. 读取人员信息导入.xlsx（E列：手机号码，F列：UUMS机构编码）
2. 根据F列UUMS机构编码查询并填充G列机构编码
3. 使用E列手机号码和G列机构编码批量创建用户账号
作者：Claude Code
创建时间：2025-07-20
更新时间：2025-07-20
"""

import pandas as pd
import requests
import json
import os
import sys
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse
import pymysql

# 配置日志 - 仅输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PersonnelProcessor:
    """人员信息处理器"""
    
    def __init__(self, base_url: str = "http://localhost:8080/jeecg-boot", token: str = None):
        """
        初始化处理器
        
        Args:
            base_url: JeecgBoot API基础URL
            token: JWT认证token
        """
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'X-Access-Token': token if token else ''
        }
        self.org_cache = {}  # 缓存查询结果，避免重复查询
        
    def login(self, username: str = "admin", password: str = "123456") -> bool:
        """
        登录获取token
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        try:
            login_url = f"{self.base_url}/sys/mLogin"
            login_data = {
                "username": username,
                "password": password
            }
            
            logger.info(f"正在登录系统... 用户名: {username}")
            response = requests.post(login_url, json=login_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                self.token = result['result']['token']
                self.headers['X-Access-Token'] = self.token
                logger.info("登录成功！")
                return True
            else:
                logger.error(f"登录失败: {result.get('message', '未知错误')}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"登录请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"登录过程发生异常: {e}")
            return False
    
    def query_department_tree(self) -> Dict:
        """
        查询部门树结构
        
        Returns:
            Dict: 部门树数据
        """
        try:
            url = f"{self.base_url}/sys/sysDepart/queryTreeList"
            logger.info("正在查询部门树结构...")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                logger.info(f"成功获取部门树，共 {len(result.get('result', []))} 个顶级部门")
                return result.get('result', [])
            else:
                logger.error(f"查询部门树失败: {result.get('message', '未知错误')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"查询部门树请求失败: {e}")
            return []
        except Exception as e:
            logger.error(f"查询部门树发生异常: {e}")
            return []
    
    def query_depart_by_org_code(self, org_code: str) -> Optional[Dict]:
        """
        根据机构编码查询sys_depart表获取部门ID和详细信息
        
        Args:
            org_code: 机构编码
            
        Returns:
            Optional[Dict]: 部门信息，包含id等字段
        """
        # 首先尝试API查询
        try:
            url = f"{self.base_url}/sys/sysDepart/list"
            params = {'orgCode': org_code}
            logger.debug(f"查询部门信息: {url}?orgCode={org_code}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                records = result.get('result', {}).get('records', [])
                if records:
                    depart_info = records[0]  # 取第一条记录
                    logger.debug(f"API查询成功: orgCode={org_code} -> id={depart_info.get('id')}, name={depart_info.get('departName')}")
                    return depart_info
                else:
                    logger.debug(f"API查询无结果: orgCode={org_code}")
                    
        except requests.RequestException as e:
            logger.debug(f"API查询失败: {e}")
        except Exception as e:
            logger.debug(f"API查询异常: {e}")
        
        # API查询失败或无结果，尝试数据库直接查询
        logger.debug(f"尝试数据库直接查询部门信息: orgCode={org_code}")
        return self.query_depart_by_org_code_via_database(org_code)
    
    def query_depart_by_org_code_via_database(self, org_code: str) -> Optional[Dict]:
        """
        通过数据库直接查询sys_depart表获取部门信息
        
        Args:
            org_code: 机构编码
            
        Returns:
            Optional[Dict]: 部门信息，包含id等字段
        """
        connection = None
        try:
            # 数据库连接配置
            db_config = {
                'host': 'localhost',
                'port': 30004,  # Docker映射端口
                'user': 'root',
                'password': 'Best@2008',
                'database': 'jeecg-boot',
                'charset': 'utf8mb4',
                'autocommit': True
            }
            
            # 建立数据库连接
            connection = pymysql.connect(**db_config)
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 查询sys_depart表
                query_sql = "SELECT id, depart_name, org_code, parent_id FROM `sys_depart` WHERE org_code = %s"
                cursor.execute(query_sql, (org_code,))
                depart_record = cursor.fetchone()
                
                if depart_record:
                    logger.debug(f"数据库查询成功: orgCode={org_code} -> id={depart_record.get('id')}, name={depart_record.get('depart_name')}")
                    return {
                        'id': depart_record.get('id'),
                        'departName': depart_record.get('depart_name'),
                        'orgCode': depart_record.get('org_code'),
                        'parentId': depart_record.get('parent_id')
                    }
                else:
                    logger.warning(f"数据库中未找到orgCode={org_code}对应的部门记录")
                    return None
                    
        except pymysql.Error as e:
            logger.error(f"数据库查询部门信息错误: {e}")
            return None
        except Exception as e:
            logger.error(f"数据库查询部门信息发生异常: {e}")
            return None
        finally:
            if connection:
                connection.close()

    def find_org_code_by_uums_code(self, uums_org_code: str, dept_tree: List[Dict]) -> Optional[str]:
        """
        根据UUMS机构编码查找对应的orgCode
        
        Args:
            uums_org_code: UUMS机构编码
            dept_tree: 部门树数据
            
        Returns:
            Optional[str]: 找到的orgCode，如果未找到返回None
        """
        if not uums_org_code:
            return None
            
        # 检查缓存
        if uums_org_code in self.org_cache:
            return self.org_cache[uums_org_code]
        
        def search_in_tree(nodes: List[Dict]) -> Optional[str]:
            """递归搜索部门树"""
            for node in nodes:
                # 检查当前节点
                if node.get('uumsOrgCode') == uums_org_code:
                    org_code = node.get('orgCode')
                    if org_code:
                        self.org_cache[uums_org_code] = org_code
                        return org_code
                
                # 搜索子节点
                children = node.get('children', [])
                if children:
                    result = search_in_tree(children)
                    if result:
                        return result
            return None
        
        result = search_in_tree(dept_tree)
        if result:
            logger.debug(f"找到映射: {uums_org_code} -> {result}")
        else:
            logger.warning(f"未找到UUMS机构编码对应的orgCode: {uums_org_code}")
            
        return result
    
    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        读取用户提供的Excel文件，保持数据格式不变
        
        Args:
            file_path: 用户指定的Excel文件路径
            
        Returns:
            pd.DataFrame: 从用户文件读取的真实数据
        """
        try:
            # 确保使用绝对路径
            abs_file_path = os.path.abspath(file_path)
            logger.info(f"📂 正在读取用户Excel文件: {abs_file_path}")
            
            # 验证文件存在
            if not os.path.exists(abs_file_path):
                raise FileNotFoundError(f"用户指定的文件不存在: {abs_file_path}")
            
            # 检查文件大小和类型
            file_size = os.path.getsize(abs_file_path)
            file_ext = os.path.splitext(abs_file_path)[1].lower()
            logger.info(f"   - 文件大小: {file_size / 1024:.2f} KB")
            logger.info(f"   - 文件类型: {file_ext}")
            
            if file_ext not in ['.xlsx', '.xls']:
                raise ValueError(f"不支持的文件格式: {file_ext}，仅支持 .xlsx 和 .xls")
            
            # 读取Excel文件数据 - 保持所有列为字符串类型以防止数字格式化
            df = None
            engines = ['openpyxl'] if file_ext == '.xlsx' else ['xlrd', 'openpyxl']
            
            for engine in engines:
                try:
                    logger.debug(f"尝试使用 {engine} 引擎读取...")
                    # 将所有列读取为字符串类型，保持原始格式
                    df = pd.read_excel(abs_file_path, engine=engine, dtype=str)
                    logger.info(f"✅ 成功使用 {engine} 引擎读取用户文件（保持原始格式）")
                    break
                except Exception as e:
                    logger.debug(f"❌ {engine} 引擎失败: {e}")
                    continue
            
            if df is None:
                raise Exception("无法读取Excel文件，请检查文件是否损坏或格式是否正确")
            
            # 验证数据完整性
            if df.empty:
                raise ValueError("Excel文件中没有数据行，请检查文件内容")
            
            # 显示实际读取的数据信息
            logger.info(f"📊 用户数据读取成功:")
            logger.info(f"   - 数据行数: {len(df)} 行")
            logger.info(f"   - 数据列数: {len(df.columns)} 列")
            logger.info(f"   - 实际列名: {list(df.columns)}")
            
            # 显示前几行数据预览（确认是真实数据）
            logger.info(f"📋 数据预览（前3行）:")
            for i, (_, row) in enumerate(df.head(3).iterrows()):
                logger.info(f"   第{i+1}行: {dict(row)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 读取用户Excel文件失败: {e}")
            raise
    
    def detect_uums_column(self, df: pd.DataFrame) -> str:
        """
        从用户Excel文件中检测F列UUMS机构编码
        
        Args:
            df: 从用户文件读取的数据框
            
        Returns:
            str: F列的列名
        """
        logger.info("🔍 正在检测用户Excel文件中的F列（UUMS机构编码）...")
        
        # 显示所有可用列名
        available_columns = list(df.columns)
        logger.info(f"用户文件中的所有列名: {available_columns}")
        
        # 检查是否有至少6列（A-F）
        if len(available_columns) < 6:
            error_msg = f"""
❌ Excel文件列数不足，期望至少6列（A-F），实际只有 {len(available_columns)} 列。

📋 当前列名: {available_columns}

💡 期望的Excel格式:
- A列: 其他数据
- B列: 其他数据  
- C列: 其他数据
- D列: 其他数据
- E列: 手机号码
- F列: UUMS机构编码
- G列: 机构编码（将自动填充）
            """
            raise ValueError(error_msg)
        
        # 返回F列（索引5）
        f_column = available_columns[5]  # F列是第6列，索引为5
        logger.info(f"✅ 检测到F列（UUMS机构编码）: '{f_column}'")
        
        # 验证F列是否包含数据
        f_column_data = df[f_column].dropna()
        if f_column_data.empty:
            logger.warning(f"⚠️ F列 '{f_column}' 中没有数据")
        else:
            logger.info(f"📋 F列包含 {len(f_column_data)} 条UUMS机构编码数据")
            # 显示F列数据示例
            sample_values = f_column_data.head(3).tolist()
            logger.info(f"📋 F列数据示例: {sample_values}")
        
        return f_column

    def process_personnel_data(self, file_path: str) -> Tuple[pd.DataFrame, str]:
        """
        处理用户提供的人员数据Excel文件
        
        Args:
            file_path: 用户指定的Excel文件路径
            
        Returns:
            Tuple[pd.DataFrame, str]: 处理后的真实数据和输出文件路径
        """
        try:
            logger.info("🚀 开始处理用户提供的人员信息数据...")
            logger.info(f"📂 用户文件路径: {os.path.abspath(file_path)}")
            
            # 1. 读取用户的真实Excel文件
            logger.info("📖 步骤 1/5: 读取用户Excel文件")
            df_original = self.read_excel_file(file_path)
            
            if df_original.empty:
                raise ValueError("用户Excel文件为空，无数据可处理")
            
            # 确认这是真实的用户数据，而不是模拟数据
            logger.info(f"✅ 确认读取到用户真实数据: {len(df_original)} 行记录")
            
            # 2. 检测用户文件中的UUMS机构编码列
            logger.info("🔍 步骤 2/5: 检测用户Excel文件中的UUMS机构编码列")
            uums_column = self.detect_uums_column(df_original)
            
            # 显示实际要处理的UUMS编码值
            uums_values = df_original[uums_column].dropna().unique()
            logger.info(f"📋 用户文件中的UUMS机构编码值: {list(uums_values)}")
            
            # 3. 获取JeecgBoot系统的部门树数据
            logger.info("🌲 步骤 3/5: 从JeecgBoot系统获取部门树结构")
            dept_tree = self.query_department_tree()
            if not dept_tree:
                raise ValueError("无法从JeecgBoot系统获取部门树数据，请检查网络连接和认证状态")
            
            # 4. 处理用户数据的机构编码映射
            logger.info("🔄 步骤 4/5: 处理用户数据的机构编码映射")
            org_codes = []
            success_count = 0
            failed_records = []
            
            logger.info(f"开始逐行处理用户的 {len(df_original)} 条人员记录...")
            
            for index, row in df_original.iterrows():
                row_num = index + 2  # Excel行号（包含表头）
                uums_org_code = row.get(uums_column, '')
                
                # 显示正在处理的行数据（确认是真实数据）
                row_preview = {col: row[col] for col in list(df_original.columns)[:3]}  # 显示前3列
                logger.debug(f"处理第 {row_num} 行数据: {row_preview}")
                
                # 处理空值
                if pd.isna(uums_org_code) or str(uums_org_code).strip() == '':
                    logger.warning(f"第 {row_num} 行: UUMS机构编码为空")
                    org_codes.append('')
                    failed_records.append(f"第{row_num}行: UUMS机构编码为空")
                    continue
                
                # 查找对应的orgCode
                uums_code_str = str(uums_org_code).strip()
                org_code = self.find_org_code_by_uums_code(uums_code_str, dept_tree)
                
                if org_code:
                    org_codes.append(org_code)
                    success_count += 1
                    logger.info(f"✅ 第 {row_num} 行: {uums_code_str} → {org_code}")
                else:
                    org_codes.append('')
                    failed_records.append(f"第{row_num}行: 未找到'{uums_code_str}'对应的orgCode")
                    logger.warning(f"❌ 第 {row_num} 行: 未找到UUMS机构编码 '{uums_code_str}' 对应的orgCode")
            
            # 在原始用户数据基础上添加机构编码到G列
            df_result = df_original.copy()
            
            # 确保有G列，如果没有则添加
            if len(df_result.columns) < 7:
                # 添加G列
                df_result.insert(6, '机构编码', org_codes)
                logger.info("✅ 已在G列添加机构编码")
            else:
                # 如果已有G列，则更新
                g_column = df_result.columns[6]  # G列是第7列，索引为6
                df_result[g_column] = org_codes
                logger.info(f"✅ 已更新G列 '{g_column}' 为机构编码")
            
            # 5. 直接更新原始Excel文件
            logger.info("💾 步骤 5/5: 更新原始Excel文件")
            original_file_path = os.path.abspath(file_path)
            
            try:
                
                # 直接覆盖原始文件，添加机构编码列，保持格式
                logger.info(f"📝 更新原始Excel文件: {original_file_path}")
                
                # 使用openpyxl保存，避免数字格式化
                from openpyxl import Workbook
                from openpyxl.utils.dataframe import dataframe_to_rows
                
                wb = Workbook()
                ws = wb.active
                
                # 写入数据，保持所有数据为文本格式
                for r in dataframe_to_rows(df_result, index=False, header=True):
                    ws.append(r)
                
                # 将所有单元格设置为文本格式
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value is not None:
                            cell.value = str(cell.value)
                            cell.number_format = '@'  # 文本格式
                
                wb.save(original_file_path)
                logger.info("✅ 原始Excel文件已更新，新增机构编码列（保持文本格式）")
                
                # 输出详细统计信息
                self._print_processing_summary(df_result, success_count, failed_records, original_file_path, uums_column)
                
                # 自动进行用户创建流程
                logger.info("\n" + "=" * 60)
                logger.info("🚀 开始用户创建流程...")
                logger.info("=" * 60)
                
                # 6. 检测用户数据列名映射
                logger.info("🔍 步骤 6/7: 检测用户数据列名映射")
                column_mapping = self.detect_user_data_columns(df_result)
                
                # 7. 批量创建用户
                logger.info("👥 步骤 7/8: 批量创建用户账号")
                user_success_count, user_failed_count, user_failed_records = self.create_users_from_data(df_result, column_mapping)
                
                # 输出用户创建统计
                self.print_user_creation_summary(user_success_count, user_failed_count, user_failed_records)
                
                # 8. 直接更新sys_user表的org_code字段
                logger.info("\n" + "=" * 60)
                logger.info("🔧 步骤 8/8: 直接更新sys_user表的org_code字段")
                logger.info("=" * 60)
                update_success_count, update_failed_count = self.update_user_org_code_directly(df_result)
                
                # 输出最终统计
                logger.info("\n" + "=" * 70)
                logger.info("🎉 脚本执行完成！最终统计:")
                logger.info(f"   📊 用户创建: 成功 {user_success_count} 个，失败 {user_failed_count} 个")
                logger.info(f"   🔧 org_code更新: 成功 {update_success_count} 个，失败 {update_failed_count} 个")
                logger.info("=" * 70)
                
                return df_result, original_file_path
                
            except Exception as e:
                # 如果更新失败，记录错误
                logger.error(f"❌ 更新原始文件失败: {e}")
                raise
            
        except Exception as e:
            logger.error(f"❌ 处理用户人员数据时发生错误: {e}")
            raise
    
    def _print_processing_summary(self, df: pd.DataFrame, success_count: int, failed_records: List[str], output_path: str, uums_column: str):
        """打印用户数据处理摘要"""
        failed_count = len(df) - success_count
        success_rate = (success_count / len(df) * 100) if len(df) > 0 else 0
        
        logger.info("=" * 80)
        logger.info("📊 Excel文件更新完成统计:")
        logger.info(f"   📂 更新的Excel文件: {output_path}")
        logger.info(f"   🔍 检测到的UUMS列: '{uums_column}'")
        logger.info(f"   📋 原始数据: {df.shape[0]} 行 x {df.shape[1] - 1} 列")
        logger.info(f"   📋 更新后数据: {df.shape[0]} 行 x {df.shape[1]} 列 (G列填充机构编码)")
        logger.info(f"   ✅ 成功映射: {success_count} 条")
        logger.info(f"   ❌ 映射失败: {failed_count} 条")
        logger.info(f"   📈 成功率: {success_rate:.1f}%")
        
        if failed_records:
            logger.info(f"\n❌ 失败记录详情:")
            for i, record in enumerate(failed_records[:10], 1):  # 只显示前10条
                logger.info(f"   {i}. {record}")
            if len(failed_records) > 10:
                logger.info(f"   ... 还有 {len(failed_records) - 10} 条失败记录")
        
        # 显示成功映射的示例
        if success_count > 0:
            logger.info(f"\n✅ 成功映射示例:")
            success_examples = []
            for index, row in df.iterrows():
                if pd.notna(row.get('机构编码', '')) and str(row.get('机构编码', '')).strip() != '':
                    uums_code = row.get(uums_column, '')
                    org_code = row.get('机构编码', '')
                    success_examples.append(f"{uums_code} → {org_code}")
                    if len(success_examples) >= 3:  # 只显示前3个示例
                        break
            
            for i, example in enumerate(success_examples, 1):
                logger.info(f"   {i}. {example}")
        
        logger.info(f"\n💡 重要提示:")
        logger.info(f"   - 原始Excel文件已直接更新，G列填充了查询到的机构编码")
        logger.info(f"   - 机构编码对应JeecgBoot系统中的部门，用于用户创建时关联部门")
        
        logger.info("=" * 80)
    
    
    
    def detect_user_data_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        检测用户数据列名映射（基于固定列位置）
        
        Args:
            df: 数据框
            
        Returns:
            Dict[str, str]: 列名映射字典
        """
        logger.info("🔍 正在检测用户数据列名映射...")
        
        available_columns = list(df.columns)
        logger.info(f"Excel列结构: {available_columns}")
        
        detected_columns = {}
        
        # C列：密码（索引2）
        if len(available_columns) >= 3:
            c_column = available_columns[2]
            detected_columns['password'] = c_column
            logger.info(f"✅ C列（密码）: '{c_column}'")
            
            # 验证C列数据
            c_data = df[c_column].dropna()
            if not c_data.empty:
                sample_passwords = c_data.head(3).tolist()
                logger.info(f"🔑 C列密码示例: {sample_passwords}")
            else:
                logger.warning(f"⚠️ C列 '{c_column}' 中没有密码数据")

        # E列：手机号码（索引4）
        if len(available_columns) >= 5:
            e_column = available_columns[4]
            detected_columns['phone'] = e_column
            logger.info(f"✅ E列（手机号码）: '{e_column}'")
            
            # 验证E列数据
            e_data = df[e_column].dropna()
            if not e_data.empty:
                sample_phones = e_data.head(3).tolist()
                logger.info(f"📱 E列手机号示例: {sample_phones}")
            else:
                logger.warning(f"⚠️ E列 '{e_column}' 中没有手机号数据")
        
        # G列：机构编码（索引6）
        if len(available_columns) >= 7:
            g_column = available_columns[6]
            logger.info(f"✅ G列（机构编码）: '{g_column}'")
        
        # 其他列的智能检测
        column_mapping_rules = {
            'username': ['用户名', 'username', '登录名', '账号', '用户账号', '登录账号'],
            'realname': ['真实姓名', 'realname', '姓名', '真名', '员工姓名', '人员姓名'],
            'email': ['邮箱', 'email', '电子邮件', '邮件', 'Email', 'E-mail'],
            'workNo': ['工号', 'workNo', '员工号', '职工号', '工作编号', '员工编号'],
            'sex': ['性别', 'sex', '男女', 'gender'],
            'post': ['职位', 'post', '职务', '岗位', '职称'],
            'birthday': ['生日', 'birthday', '出生日期', '生年月日'],
            'telephone': ['座机', 'telephone', '固话', '办公电话', '座机号']
        }
        
        # 智能匹配其他字段
        for field, possible_names in column_mapping_rules.items():
            if field in detected_columns:  # 已检测到的跳过
                continue
                
            for col_name in available_columns:
                if col_name in possible_names:
                    detected_columns[field] = col_name
                    logger.info(f"✅ 检测到 {field}: '{col_name}'")
                    break
        
        # 检查必填字段
        required_fields = ['username', 'realname', 'phone']
        missing_fields = [field for field in required_fields if field not in detected_columns]
        
        if missing_fields:
            logger.warning(f"⚠️ 未检测到必填字段: {missing_fields}")
            logger.info("将使用默认值或生成值填充")
        
        logger.info(f"📋 最终列名映射: {detected_columns}")
        return detected_columns
    
    def build_user_json(self, row: pd.Series, column_mapping: Dict[str, str], org_code: str, row_num: int) -> Dict:
        """
        构建用户创建API的JSON请求体
        
        Args:
            row: 数据行
            column_mapping: 列名映射
            org_code: 机构编码
            row_num: 行号
            
        Returns:
            Dict: API请求JSON
        """
        def get_column_value(field: str, default: str = '') -> str:
            """安全获取列值"""
            if field in column_mapping:
                col_name = column_mapping[field]
                value = row.get(col_name, default)
                if pd.isna(value):
                    return default
                return str(value).strip()
            return default
        
        # 必填字段处理
        username = get_column_value('username')
        realname = get_column_value('realname')
        
        # 使用E列手机号码
        phone = get_column_value('phone')
        if phone:
            logger.debug(f"第{row_num}行: 使用E列手机号: {phone}")
        
        # 使用G列机构编码
        final_org_code = None
        if org_code and org_code.strip():
            final_org_code = org_code.strip()
            logger.debug(f"第{row_num}行: 使用G列机构编码: {final_org_code}")
        else:
            logger.warning(f"第{row_num}行: G列机构编码为空，用户将不关联部门")
        
        # 字段验证和自动生成
        if not username:
            # 优先使用手机号作为用户名
            if phone:
                username = phone
                logger.info(f"第{row_num}行: 用户名为空，使用手机号作为用户名: {username}")
            else:
                username = f"user_{row_num:04d}"
                logger.warning(f"第{row_num}行: 用户名和手机号都为空，自动生成用户名: {username}")
        
        if not realname:
            realname = f"用户{row_num:04d}"
            logger.warning(f"第{row_num}行: 真实姓名为空，自动生成: {realname}")
            
        if not phone:
            phone = f"1380000{row_num:04d}"
            logger.warning(f"第{row_num}行: E列手机号为空，自动生成: {phone}")
        
        # 验证手机号格式
        if phone and (not phone.isdigit() or len(phone) != 11):
            logger.warning(f"第{row_num}行: 手机号格式不正确 ({phone})，可能影响用户创建")
        
        # 优化4：处理C列密码，同时设置password和confirmPassword字段
        excel_password = get_column_value('password')
        if excel_password and excel_password.strip():
            final_password = excel_password.strip()
            logger.info(f"第{row_num}行: ✅ 使用C列密码: '{final_password}'")
        else:
            final_password = "123456"  # 默认密码
            logger.info(f"第{row_num}行: ⚠️ C列密码为空，使用默认密码: '{final_password}'")
        
        # 构建基础JSON - 使用已经准备好的数据
        user_json = {
            "username": username,
            "realname": realname,
            "password": final_password,  # 使用C列密码或默认密码
            "confirmPassword": final_password,  # 确认密码与密码相同
            "phone": phone,  # 使用准备好的手机号
            "status": "1",  # 1=正常
            "userIdentity": "1"  # 1=普通成员
        }
        
        logger.info(f"第{row_num}行: ✅ JSON中添加 password='{final_password}' (来自C列)")
        logger.info(f"第{row_num}行: ✅ JSON中添加 confirmPassword='{final_password}' (与password相同)")
        
        # 优化1：添加已经准备好的机构编码 - 同时设置orgCode和selecteddeparts字段
        if final_org_code:
            user_json["orgCode"] = final_org_code
            
            # 根据本条数据对应用户username的G列机构编码查询sys_depart表获取部门ID
            depart_info = self.query_depart_by_org_code(final_org_code)
            if depart_info:
                depart_id = depart_info.get('id')
                user_json["selecteddeparts"] = depart_id
                logger.info(f"第{row_num}行: ✅ 根据用户'{username}'的G列机构编码'{final_org_code}'查询到部门ID: '{depart_id}'")
                logger.info(f"第{row_num}行: ✅ JSON中添加 selecteddeparts='{depart_id}'")
            else:
                logger.warning(f"第{row_num}行: ⚠️ 用户'{username}'的机构编码'{final_org_code}'未找到对应部门ID，仅设置orgCode")
        else:
            logger.warning(f"第{row_num}行: ❌ 用户'{username}'无有效机构编码，将不关联部门")
        
        # 优化2：增加workNo属性，值为本条数据对应用户username
        user_json["workNo"] = username
        logger.info(f"第{row_num}行: ✅ JSON中添加 workNo='{username}' (使用用户名作为工号)")
        
        # 优化3：增加email属性，值为本条数据对应用户username拼接@ha.chinamobile.com
        generated_email = f"{username}@ha.chinamobile.com"
        user_json["email"] = generated_email
        logger.info(f"第{row_num}行: ✅ JSON中添加 email='{generated_email}' (用户名@ha.chinamobile.com)")
        
        # 可选字段（如果Excel中有现有的邮箱或工号，会被上面的优化覆盖）
        # 检查是否有Excel中的邮箱字段，如果有则给出提示
        excel_email = get_column_value('email')
        if excel_email and excel_email != generated_email:
            logger.info(f"第{row_num}行: 📝 注意：Excel中的邮箱'{excel_email}'已被生成的邮箱'{generated_email}'覆盖")
            
        excel_work_no = get_column_value('workNo')
        if excel_work_no and excel_work_no != username:
            logger.info(f"第{row_num}行: 📝 注意：Excel中的工号'{excel_work_no}'已被用户名'{username}'覆盖")
            
        sex = get_column_value('sex')
        if sex:
            # 转换性别值
            if sex in ['男', '1', 'M', 'Male']:
                user_json["sex"] = "1"
            elif sex in ['女', '2', 'F', 'Female']:
                user_json["sex"] = "2"
            else:
                user_json["sex"] = "1"  # 默认男
        
        post = get_column_value('post')
        if post:
            user_json["post"] = post
            
        birthday = get_column_value('birthday')
        if birthday:
            # 简单日期格式处理
            try:
                from datetime import datetime
                if len(birthday) == 8 and birthday.isdigit():  # YYYYMMDD
                    formatted_date = f"{birthday[:4]}-{birthday[4:6]}-{birthday[6:8]}"
                    user_json["birthday"] = formatted_date
                elif '-' in birthday or '/' in birthday:
                    user_json["birthday"] = birthday
            except:
                logger.debug(f"第{row_num}行: 日期格式处理失败: {birthday}")
        
        telephone = get_column_value('telephone')
        if telephone:
            user_json["telephone"] = telephone
        
        # 最终确认JSON内容
        logger.info(f"第{row_num}行: 最终JSON内容确认:")
        logger.info(f"   - username: {user_json.get('username', 'N/A')}")
        logger.info(f"   - realname: {user_json.get('realname', 'N/A')}")
        logger.info(f"   - phone: {user_json.get('phone', 'N/A')}")
        logger.info(f"   - password: {user_json.get('password', '未设置')}")
        logger.info(f"   - confirmPassword: {user_json.get('confirmPassword', '未设置')}")
        logger.info(f"   - orgCode: {user_json.get('orgCode', '未设置')}")
        logger.info(f"   - selecteddeparts: {user_json.get('selecteddeparts', '未设置')}")
        logger.info(f"   - workNo: {user_json.get('workNo', '未设置')}")
        logger.info(f"   - email: {user_json.get('email', '未设置')}")
        
        return user_json
    
    def create_user_via_api(self, user_data: Dict, row_num: int) -> Tuple[bool, str, Dict]:
        """
        通过API创建用户
        
        Args:
            user_data: 用户数据JSON
            row_num: 行号
            
        Returns:
            Tuple[bool, str, Dict]: (是否成功, 错误信息, 响应数据)
        """
        try:
            url = f"{self.base_url}/sys/user/add"
            
            # 显示关键字段信息
            username = user_data.get('username', '')
            realname = user_data.get('realname', '')
            phone = user_data.get('phone', '')
            org_code = user_data.get('orgCode', '')
            selecteddeparts = user_data.get('selecteddeparts', '')
            
            logger.info(f"第{row_num}行: 创建用户 - 用户名: {username}, 姓名: {realname}")
            logger.info(f"第{row_num}行: 使用手机号: {phone}, 机构编码: {org_code if org_code else '无'}, 部门ID: {selecteddeparts if selecteddeparts else '无'}")
            
            logger.debug(f"第{row_num}行: 调用用户创建API: {url}")
            logger.debug(f"第{row_num}行: 完整请求数据: {json.dumps(user_data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(url, json=user_data, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"第{row_num}行: API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                logger.info(f"✅ 第{row_num}行: 用户 '{username}' 创建成功")
                logger.info(f"   📱 手机号: {phone}, 🏢 机构编码: {org_code if org_code else '无'}, 🏬 部门ID: {selecteddeparts if selecteddeparts else '无'}")
                return True, "", result
            else:
                error_msg = result.get('message', '未知错误')
                logger.error(f"❌ 第{row_num}行: 用户创建失败 - {error_msg}")
                logger.error(f"   尝试创建的数据: 用户名={username}, 手机号={phone}, 机构编码={org_code if org_code else '无'}, 部门ID={selecteddeparts if selecteddeparts else '无'}")
                return False, error_msg, result
                
        except requests.RequestException as e:
            error_msg = f"API请求失败: {e}"
            logger.error(f"❌ 第{row_num}行: {error_msg}")
            return False, error_msg, {}
        except Exception as e:
            error_msg = f"创建用户时发生异常: {e}"
            logger.error(f"❌ 第{row_num}行: {error_msg}")
            return False, error_msg, {}
    
    def create_users_from_data(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Tuple[int, int, List[str]]:
        """
        批量创建用户
        
        Args:
            df: 包含机构编码的数据框
            column_mapping: 列名映射
            
        Returns:
            Tuple[int, int, List[str]]: (成功数量, 失败数量, 失败记录)
        """
        logger.info("👥 开始批量创建用户...")
        logger.info("📋 将使用以下Excel列数据:")
        logger.info("   📱 手机号: E列（用户提供的手机号码）")
        logger.info("   🏢 机构编码: G列（已映射的JeecgBoot系统部门编码）")
        
        success_count = 0
        failed_count = 0
        failed_records = []
        
        # 只处理G列机构编码不为空的记录
        g_column = df.columns[6] if len(df.columns) > 6 else '机构编码'
        valid_data = df[df[g_column].notna() & (df[g_column] != '')].copy()
        
        if valid_data.empty:
            logger.warning(f"⚠️ 没有找到G列 '{g_column}' 不为空的记录，无法创建用户")
            return 0, 0, []
        
        logger.info(f"📊 找到 {len(valid_data)} 条有效记录（G列机构编码不为空）")
        
        # 显示将要使用的数据示例
        if len(valid_data) > 0:
            sample_row = valid_data.iloc[0]
            e_column = sample_row.index[4] if len(sample_row.index) > 4 else 'E列'
            phone_sample = sample_row.get(e_column, '无')
            org_code_sample = sample_row.get(g_column, '无')
            logger.info(f"📋 数据示例 - E列手机号: {phone_sample}, G列机构编码: {org_code_sample}")
        
        for index, row in valid_data.iterrows():
            row_num = index + 2  # Excel行号（包含表头）
            org_code = str(row[g_column]).strip()
            
            # 调试信息：显示从G列读取的机构编码
            logger.info(f"第{row_num}行: 从G列 '{g_column}' 读取机构编码: '{org_code}'")
            
            try:
                # 构建用户JSON数据
                user_data = self.build_user_json(row, column_mapping, org_code, row_num)
                
                # 调试信息：显示JSON中的机构编码和部门ID
                json_org_code = user_data.get('orgCode', '未设置')
                json_selecteddeparts = user_data.get('selecteddeparts', '未设置')
                logger.info(f"第{row_num}行: JSON中的orgCode: '{json_org_code}', selecteddeparts: '{json_selecteddeparts}'")
                
                # 调用创建API
                success, error_msg, response_data = self.create_user_via_api(user_data, row_num)
                
                if success:
                    success_count += 1
                    # 详细信息已在create_user_via_api中显示，这里只做简单计数
                else:
                    failed_count += 1
                    failed_records.append(f"第{row_num}行: {user_data.get('username', 'N/A')} (手机号: {user_data.get('phone', 'N/A')}) - {error_msg}")
                    
            except Exception as e:
                failed_count += 1
                failed_records.append(f"第{row_num}行: 数据处理异常 - {str(e)}")
                logger.error(f"❌ 第{row_num}行: 处理用户数据时发生异常: {e}")
        
        return success_count, failed_count, failed_records
    
    def print_user_creation_summary(self, success_count: int, failed_count: int, failed_records: List[str]):
        """打印用户创建统计摘要"""
        total_count = success_count + failed_count
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        logger.info("==" * 50)
        logger.info("👥 用户创建完成统计:")
        logger.info(f"   📊 处理总数: {total_count} 个用户")
        logger.info(f"   ✅ 创建成功: {success_count} 个用户")
        logger.info(f"   ❌ 创建失败: {failed_count} 个用户")
        logger.info(f"   📈 成功率: {success_rate:.1f}%")
        
        if failed_records:
            logger.info(f"\n❌ 失败记录详情:")
            for i, record in enumerate(failed_records[:10], 1):  # 只显示前10条
                logger.info(f"   {i}. {record}")
            if len(failed_records) > 10:
                logger.info(f"   ... 还有 {len(failed_records) - 10} 条失败记录")
        
        logger.info(f"\n💡 重要说明:")
        logger.info(f"   - 只有G列机构编码不为空的记录才会被创建为用户")
        logger.info(f"   - 手机号使用E列用户提供的手机号码")
        logger.info(f"   - 机构编码使用G列已映射的JeecgBoot部门编码")
        logger.info(f"   - 默认密码统一设置为: 123456")
        logger.info(f"   - 缺失的必填字段会自动生成默认值")
        logger.info(f"   - 用户状态默认为正常(1)，身份为普通成员(1)")
        
        logger.info("==" * 50)
    
    def update_user_org_code_directly(self, df: pd.DataFrame) -> Tuple[int, int]:
        """
        脚本执行完成后，直接更新sys_user表中的org_code字段
        
        Args:
            df: 包含用户数据和机构编码的DataFrame
            
        Returns:
            Tuple[int, int]: (成功更新数量, 失败更新数量)
        """
        logger.info("\n" + "=" * 60)
        logger.info("🔄 开始直接更新sys_user表的org_code字段...")
        logger.info("=" * 60)
        
        success_count = 0
        failed_count = 0
        
        # 获取列名
        username_column = df.columns[0] if len(df.columns) > 0 else '用户名'  # A列
        org_code_column = df.columns[6] if len(df.columns) > 6 else '机构编码'  # G列
        
        logger.info(f"📋 开始遍历Excel数据更新用户org_code字段:")
        logger.info(f"   - A列用户名: '{username_column}'")
        logger.info(f"   - G列机构编码: '{org_code_column}'")
        
        for index, row in df.iterrows():
            row_num = index + 2  # Excel行号（包含表头）
            username = row.get(username_column, '')
            org_code = row.get(org_code_column, '')
            
            # 跳过无效数据
            if pd.isna(username) or str(username).strip() == '':
                logger.warning(f"第{row_num}行: 用户名为空，跳过")
                continue
                
            if pd.isna(org_code) or str(org_code).strip() == '':
                logger.warning(f"第{row_num}行: 机构编码为空，跳过")
                continue
                
            username_str = str(username).strip()
            org_code_str = str(org_code).strip()
            
            try:
                # 直接通过API更新用户的org_code字段
                success = self.update_user_org_code_by_username(username_str, org_code_str, row_num)
                if success:
                    success_count += 1
                    logger.info(f"✅ 第{row_num}行: 用户 '{username_str}' 的org_code更新为 '{org_code_str}'")
                else:
                    failed_count += 1
                    logger.error(f"❌ 第{row_num}行: 用户 '{username_str}' 的org_code更新失败")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ 第{row_num}行: 更新用户 '{username_str}' 时发生异常: {e}")
        
        # 输出更新统计
        total_count = success_count + failed_count
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 sys_user表org_code字段更新完成统计:")
        logger.info(f"   📊 处理总数: {total_count} 个用户")
        logger.info(f"   ✅ 更新成功: {success_count} 个用户")
        logger.info(f"   ❌ 更新失败: {failed_count} 个用户")
        logger.info(f"   📈 成功率: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        return success_count, failed_count
    
    def update_user_org_code_by_username(self, username: str, org_code: str, row_num: int) -> bool:
        """
        根据用户名更新用户的org_code字段 - 使用数据库直接更新
        
        Args:
            username: 用户名
            org_code: 机构编码
            row_num: Excel行号
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 注意：JeecgBoot框架在SysUserController.java第204行强制设置user.setOrgCode(null)
            # 因此API更新无效，需要直接在数据库层面更新
            logger.warning(f"第{row_num}行: 注意 - JeecgBoot框架阻止通过API更新org_code字段")
            logger.info(f"第{row_num}行: 尝试使用数据库直接更新方式...")
            
            # 尝试直接数据库更新
            success = self.update_org_code_via_database(username, org_code, row_num)
            if success:
                logger.info(f"✅ 第{row_num}行: 用户 '{username}' 的org_code通过数据库直接更新为 '{org_code}'")
                return True
            else:
                logger.error(f"❌ 第{row_num}行: 数据库直接更新也失败")
                return False
                
        except Exception as e:
            logger.error(f"第{row_num}行: 更新用户发生异常: {e}")
            return False
    
    def update_org_code_via_database(self, username: str, org_code: str, row_num: int) -> bool:
        """
        通过数据库直接更新org_code字段
        
        Args:
            username: 用户名
            org_code: 机构编码
            row_num: Excel行号
            
        Returns:
            bool: 是否更新成功
        """
        connection = None
        try:
            # 数据库连接配置
            db_config = {
                'host': 'localhost',
                'port': 30004,  # Docker映射端口
                'user': 'root',
                'password': 'Best@2008',
                'database': 'jeecg-boot',
                'charset': 'utf8mb4',
                'autocommit': True  # 自动提交事务
            }
            
            logger.debug(f"第{row_num}行: 连接数据库 {db_config['host']}:{db_config['port']}")
            
            # 建立数据库连接
            connection = pymysql.connect(**db_config)
            
            with connection.cursor() as cursor:
                # 首先检查用户是否存在
                check_sql = "SELECT id, username, realname FROM `sys_user` WHERE username = %s"
                cursor.execute(check_sql, (username,))
                user_record = cursor.fetchone()
                
                if not user_record:
                    logger.error(f"第{row_num}行: 数据库中未找到用户名为 '{username}' 的用户")
                    return False
                
                user_id, db_username, realname = user_record
                logger.debug(f"第{row_num}行: 找到用户 - ID: {user_id}, 用户名: {db_username}, 姓名: {realname}")
                
                # 更新org_code字段
                update_sql = "UPDATE `sys_user` SET org_code = %s WHERE username = %s"
                rows_affected = cursor.execute(update_sql, (org_code, username))
                
                if rows_affected > 0:
                    logger.info(f"第{row_num}行: 数据库更新成功 - 用户 '{username}' 的org_code设置为 '{org_code}'")
                    
                    # 验证更新结果
                    verify_sql = "SELECT org_code FROM `sys_user` WHERE username = %s"
                    cursor.execute(verify_sql, (username,))
                    updated_org_code = cursor.fetchone()[0]
                    
                    if updated_org_code == org_code:
                        logger.info(f"第{row_num}行: ✅ 验证成功 - org_code已更新为 '{updated_org_code}'")
                        return True
                    else:
                        logger.error(f"第{row_num}行: ❌ 验证失败 - 期望: '{org_code}', 实际: '{updated_org_code}'")
                        return False
                else:
                    logger.error(f"第{row_num}行: 数据库更新失败 - 没有行被更新")
                    return False
                    
        except pymysql.Error as e:
            logger.error(f"第{row_num}行: 数据库操作错误: {e}")
            return False
        except Exception as e:
            logger.error(f"第{row_num}行: 数据库更新发生异常: {e}")
            return False
        finally:
            if connection:
                connection.close()
                logger.debug(f"第{row_num}行: 数据库连接已关闭")

    def validate_system_connection(self) -> bool:
        """
        验证系统连接状态
        
        Returns:
            bool: 连接是否正常
        """
        try:
            logger.info("🔗 验证系统连接状态...")
            
            # 测试API连接
            test_url = f"{self.base_url}/sys/user/getUserInfo"
            response = requests.get(test_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("✅ 系统连接正常，认证有效")
                    return True
                else:
                    logger.warning(f"⚠️ 系统连接正常，但认证可能无效: {result.get('message', '未知错误')}")
                    return False
            else:
                logger.error(f"❌ 系统连接失败，HTTP状态码: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ 系统连接测试失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 系统连接验证发生异常: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="人员信息处理脚本 - 根据F列UUMS机构编码查询并填充G列系统机构编码，使用E列手机号批量创建用户账号",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 create_user.py --file 人员信息导入.xlsx
  python3 create_user.py --file data.xlsx --url http://server:8080/jeecg-boot
  python3 create_user.py --file data.xlsx --verbose
        """
    )
    parser.add_argument('--file', '-f', required=True, help='输入的Excel文件路径（必填）')
    parser.add_argument('--url', default='http://localhost:8080/jeecg-boot', help='JeecgBoot API地址（默认: localhost:8080）')
    parser.add_argument('--username', '-u', default='admin', help='登录用户名（默认: admin）')
    parser.add_argument('--password', '-p', default='123456', help='登录密码（默认: 123456）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细日志输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    start_time = datetime.now()
    
    try:
        logger.info("=" * 70)
        logger.info("🚀 人员信息处理脚本启动")
        logger.info(f"📅 启动时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        # 验证输入参数
        logger.info("🔍 验证输入参数...")
        
        # 检查输入文件
        if not os.path.exists(args.file):
            logger.error(f"❌ 输入文件不存在: {args.file}")
            return 1
        
        # 获取文件绝对路径
        file_path = os.path.abspath(args.file)
        logger.info(f"📁 输入文件: {file_path}")
        logger.info(f"🌐 API地址: {args.url}")
        logger.info(f"👤 用户名: {args.username}")
        
        # 创建处理器
        logger.info("🔧 初始化处理器...")
        processor = PersonnelProcessor(base_url=args.url)
        
        # 开始处理
        logger.info("🔐 尝试登录系统...")
        if not processor.login(args.username, args.password):
            logger.error("❌ 登录失败，无法继续处理")
            logger.error("请检查:")
            logger.error("  1. 用户名和密码是否正确")
            logger.error("  2. JeecgBoot服务是否正常运行")
            logger.error("  3. 网络连接是否正常")
            return 1
        
        # 验证系统连接
        if not processor.validate_system_connection():
            logger.error("❌ 系统连接验证失败")
            return 1
        
        # 开始处理数据
        logger.info("🔄 开始处理人员信息数据...")
        df, output_path = processor.process_personnel_data(file_path)
        
        # 计算执行时间
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 Excel文件更新完成！")
        logger.info(f"⏱️  执行时间: {duration.total_seconds():.2f} 秒")
        logger.info(f"📂 更新文件: {output_path}")
        logger.info(f"📊 处理记录: {len(df)} 条")
        logger.info(f"🔄 原始文件已直接更新，无需查找新文件")
        logger.info("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ 用户中断操作")
        return 1
    except FileNotFoundError as e:
        logger.error(f"❌ 文件错误: {e}")
        return 1
    except requests.RequestException as e:
        logger.error(f"❌ 网络请求错误: {e}")
        logger.error("请检查:")
        logger.error("  1. 网络连接是否正常")
        logger.error("  2. JeecgBoot服务地址是否正确")
        logger.error("  3. 防火墙是否阻止连接")
        return 1
    except ValueError as e:
        logger.error(f"❌ 数据错误: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        logger.error("详细错误信息请查看日志文件")
        return 1
    finally:
        # 清理工作
        end_time = datetime.now() if 'end_time' not in locals() else end_time
        duration = end_time - start_time
        logger.info(f"\n📝 程序运行总计时间: {duration.total_seconds():.2f} 秒")

if __name__ == "__main__":
    sys.exit(main())