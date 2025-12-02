package org.jeecg.modules.copyright.log.entity;

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
 * @Description: 软著申请AI日志表
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Data
@TableName("copyright_log_copyrightagentlog")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="软著申请AI日志表")
public class CopyrightAgentLog implements Serializable {
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
	/**会话ID*/
	@Excel(name = "会话ID", width = 15)
    @Schema(description = "会话ID")
    private java.lang.String sessionId;
	/**Agent名称*/
	@Excel(name = "Agent名称", width = 15)
    @Schema(description = "Agent名称")
    private java.lang.String agentName;
	/**Agent类型*/
	@Excel(name = "Agent类型", width = 15)
    @Schema(description = "Agent类型")
    private java.lang.String agentType;
	/**执行阶段*/
	@Excel(name = "执行阶段", width = 15)
    @Schema(description = "执行阶段")
    private java.lang.String executionPhase;
	/**执行状态*/
	@Excel(name = "执行状态", width = 15, dicCode = "status")
	@Dict(dicCode = "status")
    @Schema(description = "执行状态")
    private java.lang.Integer status;
	/**开始时间*/
	@Excel(name = "开始时间", width = 20, format = "yyyy-MM-dd HH:mm:ss")
	@JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss")
    @Schema(description = "开始时间")
    private java.util.Date startTime;
	/**结束时间*/
	@Excel(name = "结束时间", width = 20, format = "yyyy-MM-dd HH:mm:ss")
	@JsonFormat(timezone = "GMT+8",pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss")
    @Schema(description = "结束时间")
    private java.util.Date endTime;
	/**执行时长(毫秒)*/
	@Excel(name = "执行时长(毫秒)", width = 15)
    @Schema(description = "执行时长(毫秒)")
    private java.math.BigDecimal durationMs;
	/**输入参数JSON*/
	@Excel(name = "输入参数JSON", width = 15)
    @Schema(description = "输入参数JSON")
    private java.lang.String inputParams;
	/**输出结果JSON*/
	@Excel(name = "输出结果JSON", width = 15)
    @Schema(description = "输出结果JSON")
    private java.lang.String outputResult;
	/**错误信息*/
	@Excel(name = "错误信息", width = 15)
    @Schema(description = "错误信息")
    private java.lang.String errorMessage;
	/**错误堆栈*/
	@Excel(name = "错误堆栈", width = 15)
    @Schema(description = "错误堆栈")
    private java.lang.String errorStack;
	/**重试次数*/
	@Excel(name = "重试次数", width = 15)
    @Schema(description = "重试次数")
    private java.lang.Integer retryCount;
	/**使用的模型名称*/
	@Excel(name = "使用的模型名称", width = 15)
    @Schema(description = "使用的模型名称")
    private java.lang.String modelName;
	/**总Token消耗*/
	@Excel(name = "总Token消耗", width = 15)
    @Schema(description = "总Token消耗")
    private java.lang.Integer totalTokens;
	/**Prompt Token数*/
	@Excel(name = "Prompt Token数", width = 15)
    @Schema(description = "Prompt Token数")
    private java.lang.Integer promptTokens;
	/**完成Token数*/
	@Excel(name = "完成Token数", width = 15)
    @Schema(description = "完成Token数")
    private java.lang.Integer completionTokens;
}
