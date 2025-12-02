package org.jeecg.modules.copyright.apply.entity;

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
 * @Description: 软著申请聊天会话
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Data
@TableName("copyright_apply_copyrightsession")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="软著申请聊天会话")
public class CopyrightSession implements Serializable {
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
	/**用户名*/
	@Excel(name = "用户名", width = 15)
    @Schema(description = "用户名")
    private java.lang.String username;
	/**软件名称*/
	@Excel(name = "软件名称", width = 15)
    @Schema(description = "软件名称")
    private java.lang.String softwareName;
	/**软件简称*/
	@Excel(name = "软件简称", width = 15)
    @Schema(description = "软件简称")
    private java.lang.String shortName;
	/**软件版本号*/
	@Excel(name = "软件版本号", width = 15)
    @Schema(description = "软件版本号")
    private java.lang.String version;
	/**会话状态*/
	@Excel(name = "会话状态", width = 15)
    @Schema(description = "会话状态")
    private java.lang.String status;
	/**需求JSON*/
	@Excel(name = "需求JSON", width = 15)
    @Schema(description = "需求JSON")
    private java.lang.String requirementJson;
	/**进度JSON*/
	@Excel(name = "进度JSON", width = 15)
    @Schema(description = "进度JSON")
    private java.lang.String progressJson;
	/**错误信息*/
	@Excel(name = "错误信息", width = 15)
    @Schema(description = "错误信息")
    private java.lang.String errorMessage;
	/**重试次数*/
	@Excel(name = "重试次数", width = 15)
    @Schema(description = "重试次数")
    private java.lang.Integer retryCount;
}
