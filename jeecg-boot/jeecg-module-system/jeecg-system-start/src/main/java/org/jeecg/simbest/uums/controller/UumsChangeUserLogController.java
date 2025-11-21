package org.jeecg.simbest.uums.controller;

import java.util.Arrays;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.system.query.QueryGenerator;
import org.jeecg.config.shiro.IgnoreAuth;
import org.jeecg.simbest.uums.entity.UumsChangeUserLog;
import org.jeecg.simbest.uums.scheduler.SyncUumsOrgScheduler;
import org.jeecg.simbest.uums.scheduler.SyncUumsUserScheduler;
import org.jeecg.simbest.uums.service.IUumsChangeUserLogService;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.extern.slf4j.Slf4j;

import org.jeecg.common.system.base.controller.JeecgController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.ModelAndView;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import org.jeecg.common.aspect.annotation.AutoLog;
import org.apache.shiro.authz.annotation.RequiresPermissions;
 /**
 * @Description: 主数据用户变更日志
 * @Author: jeecg-boot
 * @Date:   2025-08-13
 * @Version: V1.0
 */
@Tag(name="主数据用户变更日志")
@RestController
@RequestMapping("/uums/uumsChangeUserLog")
@Slf4j
public class UumsChangeUserLogController extends JeecgController<UumsChangeUserLog, IUumsChangeUserLogService> {
	@Autowired
	private IUumsChangeUserLogService uumsChangeUserLogService;

	 @Autowired
	 private SyncUumsUserScheduler syncUumsUserScheduler;

	 /**
	  * 同步人员
	  * http://localhost:54009/dictd/uums/uumsChangeUserLog/syncUser?startDate=2025-08-01&endDate=2025-09-01
	  *
	  * @param startDate
	  * @param endDate
	  * @return
	  */
	 @IgnoreAuth
	 @Operation(summary = "同步人员")
	 @GetMapping(value = "/syncUser")
	 public Result<String> syncUser(@RequestParam(name = "startDate") String startDate,
								   @RequestParam(name = "endDate") String endDate) {
		 try {
			 log.info("[UumsChangeUserLogController] 开始同步人员数据，时间范围: {} ~ {}", startDate, endDate);

			 // 调用Scheduler中完善的同步方法
			 syncUumsUserScheduler.syncUumsUsers(startDate, endDate);

			 return Result.OK("人员数据同步任务已启动，请查看日志了解详细进度");

		 } catch (Exception e) {
			 log.error("[UumsChangeOrgLogController] 同步人员数据异常", e);
			 return Result.error("同步人员数据失败: " + e.getMessage());
		 }
	 }

	/**
	 * 分页列表查询
	 *
	 * @param uumsChangeUserLog
	 * @param pageNo
	 * @param pageSize
	 * @param req
	 * @return
	 */
	//@AutoLog(value = "主数据用户变更日志-分页列表查询")
	@Operation(summary="主数据用户变更日志-分页列表查询")
	@GetMapping(value = "/list")
	public Result<IPage<UumsChangeUserLog>> queryPageList(UumsChangeUserLog uumsChangeUserLog,
								   @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
								   @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
								   HttpServletRequest req) {


        QueryWrapper<UumsChangeUserLog> queryWrapper = QueryGenerator.initQueryWrapper(uumsChangeUserLog, req.getParameterMap());
		Page<UumsChangeUserLog> page = new Page<UumsChangeUserLog>(pageNo, pageSize);
		IPage<UumsChangeUserLog> pageList = uumsChangeUserLogService.page(page, queryWrapper);
		return Result.OK(pageList);
	}
	
	/**
	 *   添加
	 *
	 * @param uumsChangeUserLog
	 * @return
	 */
	@AutoLog(value = "主数据用户变更日志-添加")
	@Operation(summary="主数据用户变更日志-添加")
	@RequiresPermissions("uums:us_log_uums_change_user:add")
	@PostMapping(value = "/add")
	public Result<String> add(@RequestBody UumsChangeUserLog uumsChangeUserLog) {
		uumsChangeUserLogService.save(uumsChangeUserLog);

		return Result.OK("添加成功！");
	}
	
	/**
	 *  编辑
	 *
	 * @param uumsChangeUserLog
	 * @return
	 */
	@AutoLog(value = "主数据用户变更日志-编辑")
	@Operation(summary="主数据用户变更日志-编辑")
	@RequiresPermissions("uums:us_log_uums_change_user:edit")
	@RequestMapping(value = "/edit", method = {RequestMethod.PUT,RequestMethod.POST})
	public Result<String> edit(@RequestBody UumsChangeUserLog uumsChangeUserLog) {
		uumsChangeUserLogService.updateById(uumsChangeUserLog);
		return Result.OK("编辑成功!");
	}
	
	/**
	 *   通过id删除
	 *
	 * @param id
	 * @return
	 */
	@AutoLog(value = "主数据用户变更日志-通过id删除")
	@Operation(summary="主数据用户变更日志-通过id删除")
	@RequiresPermissions("uums:us_log_uums_change_user:delete")
	@DeleteMapping(value = "/delete")
	public Result<String> delete(@RequestParam(name="id",required=true) String id) {
		uumsChangeUserLogService.removeById(id);
		return Result.OK("删除成功!");
	}
	
	/**
	 *  批量删除
	 *
	 * @param ids
	 * @return
	 */
	@AutoLog(value = "主数据用户变更日志-批量删除")
	@Operation(summary="主数据用户变更日志-批量删除")
	@RequiresPermissions("uums:us_log_uums_change_user:deleteBatch")
	@DeleteMapping(value = "/deleteBatch")
	public Result<String> deleteBatch(@RequestParam(name="ids",required=true) String ids) {
		this.uumsChangeUserLogService.removeByIds(Arrays.asList(ids.split(",")));
		return Result.OK("批量删除成功!");
	}
	
	/**
	 * 通过id查询
	 *
	 * @param id
	 * @return
	 */
	//@AutoLog(value = "主数据用户变更日志-通过id查询")
	@Operation(summary="主数据用户变更日志-通过id查询")
	@GetMapping(value = "/queryById")
	public Result<UumsChangeUserLog> queryById(@RequestParam(name="id",required=true) String id) {
		UumsChangeUserLog uumsChangeUserLog = uumsChangeUserLogService.getById(id);
		if(uumsChangeUserLog==null) {
			return Result.error("未找到对应数据");
		}
		return Result.OK(uumsChangeUserLog);
	}

    /**
    * 导出excel
    *
    * @param request
    * @param uumsChangeUserLog
    */
    @RequiresPermissions("uums:us_log_uums_change_user:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, UumsChangeUserLog uumsChangeUserLog) {
        return super.exportXls(request, uumsChangeUserLog, UumsChangeUserLog.class, "主数据用户变更日志");
    }

    /**
      * 通过excel导入数据
    *
    * @param request
    * @param response
    * @return
    */
    @RequiresPermissions("uums:us_log_uums_change_user:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        return super.importExcel(request, response, UumsChangeUserLog.class);
    }

}
