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
 * @Description: 主数据用户变更日志
 * @Author: jeecg-boot
 * @Date:   2025-08-13
 * @Version: V1.0
 */
@Data
@TableName("us_log_uums_change_user")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="主数据用户变更日志")
public class UumsChangeUserLog implements Serializable {
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
	/**用户名*/
	@Excel(name = "用户名", width = 15)
    @Schema(description = "用户名")
    private java.lang.String username;
	/**显示顺序*/
	@Excel(name = "显示顺序", width = 15)
    @Schema(description = "显示顺序")
    private java.lang.Integer displayOrder;
	/**当前组织编码20位*/
	@Excel(name = "当前组织编码20位", width = 15)
    @Schema(description = "当前组织编码20位")
    private java.lang.String currentOrgCode20;
	/**员工编号*/
	@Excel(name = "员工编号", width = 15)
    @Schema(description = "员工编号")
    private java.lang.String employeeNumber;
	/**职位名称*/
	@Excel(name = "职位名称", width = 15)
    @Schema(description = "职位名称")
    private java.lang.String positionName;
	/**真实姓名*/
	@Excel(name = "真实姓名", width = 15)
    @Schema(description = "真实姓名")
    private java.lang.String truename;
	/**变更前组织编码*/
	@Excel(name = "变更前组织编码", width = 15)
    @Schema(description = "变更前组织编码")
    private java.lang.String preOrgcode;
	/**变更后组织编码*/
	@Excel(name = "变更后组织编码", width = 15)
    @Schema(description = "变更后组织编码")
    private java.lang.String currentOrgcode;
	/**变更前职位名称*/
	@Excel(name = "变更前职位名称", width = 15)
    @Schema(description = "变更前职位名称")
    private java.lang.String prePositionName;
	/**变更后职位名称*/
	@Excel(name = "变更后职位名称", width = 15)
    @Schema(description = "变更后职位名称")
    private java.lang.String currentPositionName;
	/**首选手机号*/
	@Excel(name = "首选手机号", width = 15)
    @Schema(description = "首选手机号")
    private java.lang.String preferredMobile;
	/**邮箱*/
	@Excel(name = "邮箱", width = 15)
    @Schema(description = "邮箱")
    private java.lang.String email;
	/**备用字段1*/
	@Excel(name = "备用字段1", width = 15)
    @Schema(description = "备用字段1")
    private java.lang.String ireserved1;
	/**备用字段2*/
	@Excel(name = "备用字段2", width = 15)
    @Schema(description = "备用字段2")
    private java.lang.String ireserved2;
	/**备用字段3*/
	@Excel(name = "备用字段3", width = 15)
    @Schema(description = "备用字段3")
    private java.lang.String ireserved3;
	/**备用字段4*/
	@Excel(name = "备用字段4", width = 15)
    @Schema(description = "备用字段4")
    private java.lang.String ireserved4;
	/**备用字段5*/
	@Excel(name = "备用字段5", width = 15)
    @Schema(description = "备用字段5")
    private java.lang.String ireserved5;
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
