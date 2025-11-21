package org.jeecg.simbest.uums.controller;

import java.util.Arrays;


import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.aspect.annotation.AutoLog;
import org.jeecg.common.system.base.controller.JeecgController;
import org.jeecg.common.system.query.QueryGenerator;
import org.jeecg.config.shiro.IgnoreAuth;
import org.jeecg.simbest.config.AppConfig;
import org.jeecg.simbest.uums.entity.UumsChangeOrgLog;
import org.jeecg.simbest.uums.scheduler.SyncUumsOrgScheduler;
import org.jeecg.simbest.uums.service.IUumsChangeOrgLogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.ModelAndView;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;

/**
 * @Description: 主数据组织变更日志
 * @Author: jeecg-boot
 * @Date: 2025-08-13
 * @Version: V1.0
 */
@Tag(name = "主数据组织变更日志")
@RestController
@RequestMapping("/uums/uumsChangeOrgLog")
@Slf4j
public class UumsChangeOrgLogController extends JeecgController<UumsChangeOrgLog, IUumsChangeOrgLogService> {
	@Autowired
	private IUumsChangeOrgLogService uumsChangeOrgLogService;

	@Autowired
	private SyncUumsOrgScheduler syncUumsOrgScheduler;

	/**
	 * 同步组织
	 * http://localhost:54009/dictd/uums/uumsChangeOrgLog/syncOrg?startDate=2025-08-01&endDate=2025-09-01
	 *
	 * @param startDate
	 * @param endDate
	 * @return
	 */
	@IgnoreAuth
	@Operation(summary = "同步组织")
	@GetMapping(value = "/syncOrg")
	public Result<String> syncOrg(@RequestParam(name = "startDate") String startDate,
			@RequestParam(name = "endDate") String endDate) {
		try {
			log.info("[UumsChangeOrgLogController] 开始同步组织数据，时间范围: {} ~ {}", startDate, endDate);

			// 调用Scheduler中完善的同步方法
			syncUumsOrgScheduler.syncUumsOrgs(startDate, endDate);

			return Result.OK("组织数据同步任务已启动，请查看日志了解详细进度");

		} catch (Exception e) {
			log.error("[UumsChangeOrgLogController] 同步组织数据异常", e);
			return Result.error("同步组织数据失败: " + e.getMessage());
		}
	}

	/**
	 * 分页列表查询
	 *
	 * @param uumsChangeOrgLog
	 * @param pageNo
	 * @param pageSize
	 * @param req
	 * @return
	 */
	// @AutoLog(value = "主数据组织变更日志-分页列表查询")
	@Operation(summary = "主数据组织变更日志-分页列表查询")
	@GetMapping(value = "/list")
	public Result<IPage<UumsChangeOrgLog>> queryPageList(UumsChangeOrgLog uumsChangeOrgLog,
			@RequestParam(name = "pageNo", defaultValue = "1") Integer pageNo,
			@RequestParam(name = "pageSize", defaultValue = "10") Integer pageSize,
			HttpServletRequest req) {

		QueryWrapper<UumsChangeOrgLog> queryWrapper = QueryGenerator.initQueryWrapper(uumsChangeOrgLog,
				req.getParameterMap());
		Page<UumsChangeOrgLog> page = new Page<UumsChangeOrgLog>(pageNo, pageSize);
		IPage<UumsChangeOrgLog> pageList = uumsChangeOrgLogService.page(page, queryWrapper);
		return Result.OK(pageList);
	}

	/**
	 * 添加
	 *
	 * @param uumsChangeOrgLog
	 * @return
	 */
	@AutoLog(value = "主数据组织变更日志-添加")
	@Operation(summary = "主数据组织变更日志-添加")
	@RequiresPermissions("uums:us_log_uums_change_org:add")
	@PostMapping(value = "/add")
	public Result<String> add(@RequestBody UumsChangeOrgLog uumsChangeOrgLog) {
		uumsChangeOrgLogService.save(uumsChangeOrgLog);

		return Result.OK("添加成功！");
	}

	/**
	 * 编辑
	 *
	 * @param uumsChangeOrgLog
	 * @return
	 */
	@AutoLog(value = "主数据组织变更日志-编辑")
	@Operation(summary = "主数据组织变更日志-编辑")
	@RequiresPermissions("uums:us_log_uums_change_org:edit")
	@RequestMapping(value = "/edit", method = { RequestMethod.PUT, RequestMethod.POST })
	public Result<String> edit(@RequestBody UumsChangeOrgLog uumsChangeOrgLog) {
		uumsChangeOrgLogService.updateById(uumsChangeOrgLog);
		return Result.OK("编辑成功!");
	}

	/**
	 * 通过id删除
	 *
	 * @param id
	 * @return
	 */
	@AutoLog(value = "主数据组织变更日志-通过id删除")
	@Operation(summary = "主数据组织变更日志-通过id删除")
	@RequiresPermissions("uums:us_log_uums_change_org:delete")
	@DeleteMapping(value = "/delete")
	public Result<String> delete(@RequestParam(name = "id", required = true) String id) {
		uumsChangeOrgLogService.removeById(id);
		return Result.OK("删除成功!");
	}

	/**
	 * 批量删除
	 *
	 * @param ids
	 * @return
	 */
	@AutoLog(value = "主数据组织变更日志-批量删除")
	@Operation(summary = "主数据组织变更日志-批量删除")
	@RequiresPermissions("uums:us_log_uums_change_org:deleteBatch")
	@DeleteMapping(value = "/deleteBatch")
	public Result<String> deleteBatch(@RequestParam(name = "ids", required = true) String ids) {
		this.uumsChangeOrgLogService.removeByIds(Arrays.asList(ids.split(",")));
		return Result.OK("批量删除成功!");
	}

	/**
	 * 通过id查询
	 *
	 * @param id
	 * @return
	 */
	// @AutoLog(value = "主数据组织变更日志-通过id查询")
	@Operation(summary = "主数据组织变更日志-通过id查询")
	@GetMapping(value = "/queryById")
	public Result<UumsChangeOrgLog> queryById(@RequestParam(name = "id", required = true) String id) {
		UumsChangeOrgLog uumsChangeOrgLog = uumsChangeOrgLogService.getById(id);
		if (uumsChangeOrgLog == null) {
			return Result.error("未找到对应数据");
		}
		return Result.OK(uumsChangeOrgLog);
	}

	/**
	 * 导出excel
	 *
	 * @param request
	 * @param uumsChangeOrgLog
	 */
	@RequiresPermissions("uums:us_log_uums_change_org:exportXls")
	@RequestMapping(value = "/exportXls")
	public ModelAndView exportXls(HttpServletRequest request, UumsChangeOrgLog uumsChangeOrgLog) {
		return super.exportXls(request, uumsChangeOrgLog, UumsChangeOrgLog.class, "主数据组织变更日志");
	}

	/**
	 * 通过excel导入数据
	 *
	 * @param request
	 * @param response
	 * @return
	 */
	@RequiresPermissions("uums:us_log_uums_change_org:importExcel")
	@RequestMapping(value = "/importExcel", method = RequestMethod.POST)
	public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
		return super.importExcel(request, response, UumsChangeOrgLog.class);
	}

}
