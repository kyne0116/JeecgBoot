package org.jeecg.modules.copyright.log.controller;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.system.query.QueryGenerator;
import org.jeecg.common.system.query.QueryRuleEnum;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.copyright.log.entity.CopyrightAgentLog;
import org.jeecg.modules.copyright.log.service.ICopyrightAgentLogService;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.extern.slf4j.Slf4j;

import org.jeecgframework.poi.excel.ExcelImportUtil;
import org.jeecgframework.poi.excel.def.NormalExcelConstants;
import org.jeecgframework.poi.excel.entity.ExportParams;
import org.jeecgframework.poi.excel.entity.ImportParams;
import org.jeecgframework.poi.excel.view.JeecgEntityExcelView;
import org.jeecg.common.system.base.controller.JeecgController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.multipart.MultipartHttpServletRequest;
import org.springframework.web.servlet.ModelAndView;
import com.alibaba.fastjson.JSON;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import org.jeecg.common.aspect.annotation.AutoLog;
import org.apache.shiro.authz.annotation.RequiresPermissions;
 /**
 * @Description: 软著申请AI日志表
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Tag(name="软著申请AI日志表")
@RestController
@RequestMapping("/log/copyrightAgentLog")
@Slf4j
public class CopyrightAgentLogController extends JeecgController<CopyrightAgentLog, ICopyrightAgentLogService> {
	@Autowired
	private ICopyrightAgentLogService copyrightAgentLogService;
	
	/**
	 * 分页列表查询
	 *
	 * @param copyrightAgentLog
	 * @param pageNo
	 * @param pageSize
	 * @param req
	 * @return
	 */
	//@AutoLog(value = "软著申请AI日志表-分页列表查询")
	@Operation(summary="软著申请AI日志表-分页列表查询")
	@GetMapping(value = "/list")
	public Result<IPage<CopyrightAgentLog>> queryPageList(CopyrightAgentLog copyrightAgentLog,
								   @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
								   @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
								   HttpServletRequest req) {


        // 自定义查询规则
        Map<String, QueryRuleEnum> customeRuleMap = new HashMap<>();
        // 自定义多选的查询规则为：LIKE_WITH_OR
        customeRuleMap.put("status", QueryRuleEnum.LIKE_WITH_OR);
        QueryWrapper<CopyrightAgentLog> queryWrapper = QueryGenerator.initQueryWrapper(copyrightAgentLog, req.getParameterMap(),customeRuleMap);
		Page<CopyrightAgentLog> page = new Page<CopyrightAgentLog>(pageNo, pageSize);
		IPage<CopyrightAgentLog> pageList = copyrightAgentLogService.page(page, queryWrapper);
		return Result.OK(pageList);
	}
	
	/**
	 *   添加
	 *
	 * @param copyrightAgentLog
	 * @return
	 */
	@AutoLog(value = "软著申请AI日志表-添加")
	@Operation(summary="软著申请AI日志表-添加")
	@RequiresPermissions("log:copyright_log_copyrightagentlog:add")
	@PostMapping(value = "/add")
	public Result<String> add(@RequestBody CopyrightAgentLog copyrightAgentLog) {
		copyrightAgentLogService.save(copyrightAgentLog);

		return Result.OK("添加成功！");
	}
	
	/**
	 *  编辑
	 *
	 * @param copyrightAgentLog
	 * @return
	 */
	@AutoLog(value = "软著申请AI日志表-编辑")
	@Operation(summary="软著申请AI日志表-编辑")
	@RequiresPermissions("log:copyright_log_copyrightagentlog:edit")
	@RequestMapping(value = "/edit", method = {RequestMethod.PUT,RequestMethod.POST})
	public Result<String> edit(@RequestBody CopyrightAgentLog copyrightAgentLog) {
		copyrightAgentLogService.updateById(copyrightAgentLog);
		return Result.OK("编辑成功!");
	}
	
	/**
	 *   通过id删除
	 *
	 * @param id
	 * @return
	 */
	@AutoLog(value = "软著申请AI日志表-通过id删除")
	@Operation(summary="软著申请AI日志表-通过id删除")
	@RequiresPermissions("log:copyright_log_copyrightagentlog:delete")
	@DeleteMapping(value = "/delete")
	public Result<String> delete(@RequestParam(name="id",required=true) String id) {
		copyrightAgentLogService.removeById(id);
		return Result.OK("删除成功!");
	}
	
	/**
	 *  批量删除
	 *
	 * @param ids
	 * @return
	 */
	@AutoLog(value = "软著申请AI日志表-批量删除")
	@Operation(summary="软著申请AI日志表-批量删除")
	@RequiresPermissions("log:copyright_log_copyrightagentlog:deleteBatch")
	@DeleteMapping(value = "/deleteBatch")
	public Result<String> deleteBatch(@RequestParam(name="ids",required=true) String ids) {
		this.copyrightAgentLogService.removeByIds(Arrays.asList(ids.split(",")));
		return Result.OK("批量删除成功!");
	}
	
	/**
	 * 通过id查询
	 *
	 * @param id
	 * @return
	 */
	//@AutoLog(value = "软著申请AI日志表-通过id查询")
	@Operation(summary="软著申请AI日志表-通过id查询")
	@GetMapping(value = "/queryById")
	public Result<CopyrightAgentLog> queryById(@RequestParam(name="id",required=true) String id) {
		CopyrightAgentLog copyrightAgentLog = copyrightAgentLogService.getById(id);
		if(copyrightAgentLog==null) {
			return Result.error("未找到对应数据");
		}
		return Result.OK(copyrightAgentLog);
	}

    /**
    * 导出excel
    *
    * @param request
    * @param copyrightAgentLog
    */
    @RequiresPermissions("log:copyright_log_copyrightagentlog:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, CopyrightAgentLog copyrightAgentLog) {
        return super.exportXls(request, copyrightAgentLog, CopyrightAgentLog.class, "软著申请AI日志表");
    }

    /**
      * 通过excel导入数据
    *
    * @param request
    * @param response
    * @return
    */
    @RequiresPermissions("log:copyright_log_copyrightagentlog:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        return super.importExcel(request, response, CopyrightAgentLog.class);
    }

}
