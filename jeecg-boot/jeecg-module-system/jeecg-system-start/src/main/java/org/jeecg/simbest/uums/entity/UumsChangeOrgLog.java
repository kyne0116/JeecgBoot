package org.jeecg.simbest.uums.entity;

import java.io.Serializable;
import java.io.UnsupportedEncodingException;
import java.util.Date;
import java.math.BigDecimal;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import org.jeecg.common.constant.ProvinceCityArea;
import org.jeecg.common.util.SpringContextUtils;
import lombok.Data;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;
import org.jeecgframework.poi.excel.annotation.Excel;
import org.jeecg.common.aspect.annotation.Dict;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

/**
 * @Description: 主数据组织变更日志
 * @Author: jeecg-boot
 * @Date:   2025-08-13
 * @Version: V1.0
 */
@Data
@TableName("us_log_uums_change_org")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="主数据组织变更日志")
public class UumsChangeOrgLog implements Serializable {
    private static final long serialVersionUID = 1L;

	/**主键*/
	@TableId(type = IdType.ASSIGN_ID)
    @Schema(description = "主键")
    private java.lang.String id;
	/**创建人*/
    @Schema(description = "创建人")
    private java.lang.String createBy;
	/**创建日期*/
	@JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss")
    @Schema(description = "创建日期")
    private java.util.Date createTime;
	/**更新人*/
    @Schema(description = "更新人")
    private java.lang.String updateBy;
	/**更新时间*/
	@JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss")
    @Schema(description = "更新时间")
    private java.util.Date updateTime;
	/**所属部门*/
    @Schema(description = "所属部门")
    private java.lang.String sysOrgCode;
	/**删除标志*/
	@Excel(name = "删除标志", width = 15)
    @Schema(description = "删除标志")
    @TableLogic
    private java.lang.Integer delFlag;
	/**变更类型*/
	@Excel(name = "变更类型", width = 15)
    @Schema(description = "变更类型")
    private java.lang.String changeType;
	/**变更前组织名称*/
	@Excel(name = "变更前组织名称", width = 15)
    @Schema(description = "变更前组织名称")
    private java.lang.String preOrgname;
	/**组织名称*/
	@Excel(name = "组织名称", width = 15)
    @Schema(description = "组织名称")
    private java.lang.String orgname;
	/**组织代码*/
	@Excel(name = "组织代码", width = 15)
    @Schema(description = "组织代码")
    private java.lang.String orgcode;
	/**20位组织代码*/
	@Excel(name = "20位组织代码", width = 15)
    @Schema(description = "20位组织代码")
    private java.lang.String orgcode20;
	/**组织类型*/
	@Excel(name = "组织类型", width = 15)
    @Schema(description = "组织类型")
    private java.lang.String orgtype;
	/**上级组织名称*/
	@Excel(name = "上级组织名称", width = 15)
    @Schema(description = "上级组织名称")
    private java.lang.String parentOrgname;
	/**上级组织代码*/
	@Excel(name = "上级组织代码", width = 15)
    @Schema(description = "上级组织代码")
    private java.lang.String parentOrgcode;
	/**上级20位组织代码*/
	@Excel(name = "上级20位组织代码", width = 15)
    @Schema(description = "上级20位组织代码")
    private java.lang.String parentOrgcode20;
	/**显示名称*/
	@Excel(name = "显示名称", width = 15)
    @Schema(description = "显示名称")
    private java.lang.String displayName;
	/**显示顺序*/
	@Excel(name = "显示顺序", width = 15)
    @Schema(description = "显示顺序")
    private java.lang.Integer displayOrder;
	/**层级字典值*/
	@Excel(name = "层级字典值", width = 15)
    @Schema(description = "层级字典值")
    private java.lang.String levelDictValue;
	/**处理结果*/
	@Excel(name = "处理结果", width = 15)
    @Schema(description = "处理结果")
    private java.lang.String result;
	/**同步状态*/
	@Excel(name = "同步状态", width = 15)
    @Schema(description = "同步状态")
    @Dict(dicCode = "success_fail")
    private java.lang.String resultFlag;
	/**同步日期*/
	@Excel(name = "同步日期", width = 15, format = "yyyy-MM-dd")
	@JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd")
    @DateTimeFormat(pattern="yyyy-MM-dd")
    @Schema(description = "同步日期")
    private java.util.Date syncDate;
}
