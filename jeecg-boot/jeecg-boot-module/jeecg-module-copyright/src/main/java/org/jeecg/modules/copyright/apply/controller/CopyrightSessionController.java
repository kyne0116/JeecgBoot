package org.jeecg.modules.copyright.apply.controller;

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
import org.jeecg.modules.copyright.apply.entity.CopyrightSession;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;

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
 * @Description: 软著申请申请会话
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Tag(name="软著申请会话管理")
@RestController
@RequestMapping("/copyright/session")
@Slf4j
public class CopyrightSessionController extends JeecgController<CopyrightSession, ICopyrightSessionService> {
	@Autowired
	private ICopyrightSessionService copyrightSessionService;

	// ============= 自定义业务接口 =============

	/**
	 * 创建新会话
	 *
	 * @param username 用户名
	 * @return 会话对象
	 */
	@AutoLog(value = "软著申请会话-创建会话")
	@Operation(summary="创建新会话")
	@PostMapping(value = "/create")
	public Result<CopyrightSession> createSession(@RequestParam(name="username", required=true) String username) {
		log.info("[CopyrightSessionController] 创建会话, username: {}", username);

		try {
			CopyrightSession session = copyrightSessionService.createSession(username);
			return Result.OK("会话创建成功", session);
		} catch (Exception e) {
			log.error("[CopyrightSessionController] 创建会话失败", e);
			return Result.error("会话创建失败: " + e.getMessage());
		}
	}

	/**
	 * 获取用户的会话列表（分页）
	 *
	 * @param username 用户名
	 * @param pageNo 页码
	 * @param pageSize 每页大小
	 * @return 分页结果
	 */
	@Operation(summary="获取用户会话列表")
	@GetMapping(value = "/user/{username}")
	public Result<IPage<CopyrightSession>> getUserSessions(
			@PathVariable("username") String username,
			@RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
			@RequestParam(name="pageSize", defaultValue="10") Integer pageSize) {

		log.info("[CopyrightSessionController] 查询用户会话列表, username: {}, page: {}/{}", username, pageNo, pageSize);

		Page<CopyrightSession> page = new Page<>(pageNo, pageSize);
		IPage<CopyrightSession> pageList = copyrightSessionService.getUserSessions(username, page);

		return Result.OK(pageList);
	}

	/**
	 * 获取会话详情
	 *
	 * @param sessionId 会话ID
	 * @return 会话对象
	 */
	@Operation(summary="获取会话详情")
	@GetMapping(value = "/detail/{sessionId}")
	public Result<CopyrightSession> getSessionDetail(@PathVariable("sessionId") String sessionId) {
		log.info("[CopyrightSessionController] 查询会话详情, sessionId: {}", sessionId);

		CopyrightSession session = copyrightSessionService.getSessionDetail(sessionId);
		if (session == null) {
			return Result.error("会话不存在或已删除");
		}

		return Result.OK(session);
	}

	/**
	 * 更新会话状态
	 *
	 * @param sessionId 会话ID
	 * @param status 新状态(CLARIFYING/GENERATING/CHECKING/COMPLETED/FAILED)
	 * @param errorMessage 错误信息(可选)
	 * @return 操作结果
	 */
	@AutoLog(value = "软著申请会话-更新状态")
	@Operation(summary="更新会话状态")
	@PutMapping(value = "/{sessionId}/status")
	public Result<String> updateSessionStatus(
			@PathVariable("sessionId") String sessionId,
			@RequestParam(name="status", required=true) String status,
			@RequestParam(name="errorMessage", required=false) String errorMessage) {

		log.info("[CopyrightSessionController] 更新会话状态, sessionId: {}, status: {}", sessionId, status);

		boolean updated = copyrightSessionService.updateSessionStatus(sessionId, status, errorMessage);
		if (updated) {
			return Result.OK("状态更新成功");
		} else {
			return Result.error("状态更新失败");
		}
	}

	/**
	 * 更新会话需求JSON
	 *
	 * @param sessionId 会话ID
	 * @param requirementJson 需求JSON字符串
	 * @return 操作结果
	 */
	@AutoLog(value = "软著申请会话-更新需求")
	@Operation(summary="更新会话需求")
	@PutMapping(value = "/{sessionId}/requirement")
	public Result<String> updateRequirement(
			@PathVariable("sessionId") String sessionId,
			@RequestBody String requirementJson) {

		log.info("[CopyrightSessionController] 更新会话需求, sessionId: {}", sessionId);

		boolean updated = copyrightSessionService.updateRequirement(sessionId, requirementJson);
		if (updated) {
			return Result.OK("需求更新成功");
		} else {
			return Result.error("需求更新失败");
		}
	}

	// ============= JeecgBoot标准CRUD接口 =============

	/**
	 * 分页列表查询
	 *
	 * @param copyrightSession
	 * @param pageNo
	 * @param pageSize
	 * @param req
	 * @return
	 */
	//@AutoLog(value = "软著申请会话-分页列表查询")
	@Operation(summary="软著申请会话-分页列表查询")
	@GetMapping(value = "/list")
	public Result<IPage<CopyrightSession>> queryPageList(CopyrightSession copyrightSession,
								   @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
								   @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
								   HttpServletRequest req) {


        QueryWrapper<CopyrightSession> queryWrapper = QueryGenerator.initQueryWrapper(copyrightSession, req.getParameterMap());
		Page<CopyrightSession> page = new Page<CopyrightSession>(pageNo, pageSize);
		IPage<CopyrightSession> pageList = copyrightSessionService.page(page, queryWrapper);
		return Result.OK(pageList);
	}
	
	/**
	 *   添加
	 *
	 * @param copyrightSession
	 * @return
	 */
	@AutoLog(value = "软著申请申请会话-添加")
	@Operation(summary="软著申请申请会话-添加")
	@RequiresPermissions("apply:copyright_apply_copyrightsession:add")
	@PostMapping(value = "/add")
	public Result<String> add(@RequestBody CopyrightSession copyrightSession) {
		copyrightSessionService.save(copyrightSession);

		return Result.OK("添加成功！");
	}
	
	/**
	 *  编辑
	 *
	 * @param copyrightSession
	 * @return
	 */
	@AutoLog(value = "软著申请申请会话-编辑")
	@Operation(summary="软著申请申请会话-编辑")
	@RequiresPermissions("apply:copyright_apply_copyrightsession:edit")
	@RequestMapping(value = "/edit", method = {RequestMethod.PUT,RequestMethod.POST})
	public Result<String> edit(@RequestBody CopyrightSession copyrightSession) {
		copyrightSessionService.updateById(copyrightSession);
		return Result.OK("编辑成功!");
	}
	
	/**
	 *   通过id删除
	 *
	 * @param id
	 * @return
	 */
	@AutoLog(value = "软著申请申请会话-通过id删除")
	@Operation(summary="软著申请申请会话-通过id删除")
	@RequiresPermissions("apply:copyright_apply_copyrightsession:delete")
	@DeleteMapping(value = "/delete")
	public Result<String> delete(@RequestParam(name="id",required=true) String id) {
		copyrightSessionService.removeById(id);
		return Result.OK("删除成功!");
	}
	
	/**
	 *  批量删除
	 *
	 * @param ids
	 * @return
	 */
	@AutoLog(value = "软著申请申请会话-批量删除")
	@Operation(summary="软著申请申请会话-批量删除")
	@RequiresPermissions("apply:copyright_apply_copyrightsession:deleteBatch")
	@DeleteMapping(value = "/deleteBatch")
	public Result<String> deleteBatch(@RequestParam(name="ids",required=true) String ids) {
		this.copyrightSessionService.removeByIds(Arrays.asList(ids.split(",")));
		return Result.OK("批量删除成功!");
	}
	
	/**
	 * 通过id查询
	 *
	 * @param id
	 * @return
	 */
	//@AutoLog(value = "软著申请申请会话-通过id查询")
	@Operation(summary="软著申请申请会话-通过id查询")
	@GetMapping(value = "/queryById")
	public Result<CopyrightSession> queryById(@RequestParam(name="id",required=true) String id) {
		CopyrightSession copyrightSession = copyrightSessionService.getById(id);
		if(copyrightSession==null) {
			return Result.error("未找到对应数据");
		}
		return Result.OK(copyrightSession);
	}

    /**
    * 导出excel
    *
    * @param request
    * @param copyrightSession
    */
    @RequiresPermissions("apply:copyright_apply_copyrightsession:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, CopyrightSession copyrightSession) {
        return super.exportXls(request, copyrightSession, CopyrightSession.class, "软著申请申请会话");
    }

    /**
      * 通过excel导入数据
    *
    * @param request
    * @param response
    * @return
    */
    @RequiresPermissions("apply:copyright_apply_copyrightsession:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        return super.importExcel(request, response, CopyrightSession.class);
    }

}
