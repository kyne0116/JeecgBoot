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
 * @Description: 软著申请配置表
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Data
@TableName("copyright_apply_copyrightconfig")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="软著申请配置表")
public class CopyrightConfig implements Serializable {
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
	/**配置键*/
	@Excel(name = "配置键", width = 15)
    @Schema(description = "配置键")
    private java.lang.String configKey;
	/**配置值*/
	@Excel(name = "配置值", width = 15)
    @Schema(description = "配置值")
    private java.lang.String configValue;
	/**配置类型*/
	@Excel(name = "配置类型", width = 15)
    @Schema(description = "配置类型")
    private java.lang.String configType;
	/**配置分组*/
	@Excel(name = "配置分组", width = 15)
    @Schema(description = "配置分组")
    private java.lang.String configGroup;
	/**配置描述*/
	@Excel(name = "配置描述", width = 15)
    @Schema(description = "配置描述")
    private java.lang.String description;
	/**是否系统配置*/
	@Excel(name = "是否系统配置", width = 15, dicCode = "yn")
	@Dict(dicCode = "yn")
    @Schema(description = "是否系统配置")
    private java.lang.Integer isSystem;
	/**是否加密存储*/
	@Excel(name = "是否加密存储", width = 15, dicCode = "yn")
	@Dict(dicCode = "yn")
    @Schema(description = "是否加密存储")
    private java.lang.Integer isEncrypted;
	/**排序顺序*/
	@Excel(name = "排序顺序", width = 15)
    @Schema(description = "排序顺序")
    private java.lang.Integer sortOrder;
	/**状态*/
	@Excel(name = "状态", width = 15, dicCode = "status")
	@Dict(dicCode = "status")
    @Schema(description = "状态")
    private java.lang.Integer status;
}
