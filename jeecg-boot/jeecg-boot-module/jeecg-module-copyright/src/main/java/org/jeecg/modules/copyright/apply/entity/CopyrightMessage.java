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
 * @Description: 软著申请聊天记录
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Data
@TableName("copyright_apply_copyrightmessage")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="软著申请聊天记录")
public class CopyrightMessage implements Serializable {
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
	/**对话ID*/
	@Excel(name = "对话ID", width = 15)
    @Schema(description = "对话ID")
    private java.lang.String sessionId;
	/**消息序号*/
	@Excel(name = "消息序号", width = 15)
    @Schema(description = "消息序号")
    private java.lang.Integer sequenceNo;
	/**角色*/
	@Excel(name = "角色", width = 15)
    @Schema(description = "角色")
    private java.lang.String role;
	/**消息内容*/
	@Excel(name = "消息内容", width = 15)
    @Schema(description = "消息内容")
    private java.lang.String content;
	/**消息类型*/
	@Excel(name = "消息类型", width = 15)
    @Schema(description = "消息类型")
    private java.lang.String messageType;
	/**Agent名称*/
	@Excel(name = "Agent名称", width = 15)
    @Schema(description = "Agent名称")
    private java.lang.String agentName;
}
