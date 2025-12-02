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
 * @Description: 软著文件记录
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Data
@TableName("copyright_apply_copyrightfile")
@Accessors(chain = true)
@EqualsAndHashCode(callSuper = false)
@Schema(description="软著文件记录")
public class CopyrightFile implements Serializable {
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
	/**文件类型*/
	@Excel(name = "文件类型", width = 15)
    @Schema(description = "文件类型")
    private java.lang.String fileType;
	/**文件分类*/
	@Excel(name = "文件分类", width = 15)
    @Schema(description = "文件分类")
    private java.lang.String fileCategory;
	/**文件名*/
	@Excel(name = "文件名", width = 15)
    @Schema(description = "文件名")
    private java.lang.String filename;
	/**文件路径*/
	@Excel(name = "文件路径", width = 15)
    @Schema(description = "文件路径")
    private java.lang.String filePath;
	/**文件大小(字节)*/
	@Excel(name = "文件大小(字节)", width = 15)
    @Schema(description = "文件大小(字节)")
    private java.math.BigDecimal fileSize;
	/**MIME类型*/
	@Excel(name = "MIME类型", width = 15)
    @Schema(description = "MIME类型")
    private java.lang.String mimeType;
	/**文件扩展名*/
	@Excel(name = "文件扩展名", width = 15)
    @Schema(description = "文件扩展名")
    private java.lang.String fileExtension;
	/**质量状态*/
	@Excel(name = "质量状态", width = 15)
    @Schema(description = "质量状态")
    private java.lang.String qualityStatus;
	/**质量得分(0-100)*/
	@Excel(name = "质量得分(0-100)", width = 15)
    @Schema(description = "质量得分(0-100)")
    private java.lang.Integer qualityScore;
	/**质检报告JSON*/
	@Excel(name = "质检报告JSON", width = 15)
    @Schema(description = "质检报告JSON")
    private java.lang.String qualityReportJson;
	/**代码行数(仅代码文件)*/
	@Excel(name = "代码行数(仅代码文件)", width = 15)
    @Schema(description = "代码行数(仅代码文件)")
    private java.lang.Integer codeLines;
	/**文档字数*/
	@Excel(name = "文档字数", width = 15)
    @Schema(description = "文档字数")
    private java.lang.Integer docWordCount;
}
