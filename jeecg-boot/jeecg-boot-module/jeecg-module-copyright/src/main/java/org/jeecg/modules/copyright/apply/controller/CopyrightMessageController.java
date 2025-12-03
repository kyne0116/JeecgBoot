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
import org.jeecg.modules.copyright.apply.entity.CopyrightMessage;
import org.jeecg.modules.copyright.apply.service.ICopyrightMessageService;

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
 * @Description: 软著申请聊天记录管理
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Tag(name="软著申请消息管理")
@RestController
@RequestMapping("/copyright/message")
@Slf4j
public class CopyrightMessageController extends JeecgController<CopyrightMessage, ICopyrightMessageService> {
	@Autowired
	private ICopyrightMessageService copyrightMessageService;

	// ============= 自定义业务接口 =============

	/**
	 * 保存对话消息
	 *
	 * @param sessionId   会话ID
	 * @param role        角色(user/assistant/system)
	 * @param content     消息内容
	 * @param messageType 消息类型(可选,默认text)
	 * @param agentName   Agent名称(可选)
	 * @return 保存的消息对象
	 */
	@AutoLog(value = "软著申请消息-保存消息")
	@Operation(summary="保存对话消息")
	@PostMapping(value = "/save")
	public Result<CopyrightMessage> saveMessage(
			@RequestParam(name="sessionId", required=true) String sessionId,
			@RequestParam(name="role", required=true) String role,
			@RequestParam(name="content", required=true) String content,
			@RequestParam(name="messageType", required=false, defaultValue="text") String messageType,
			@RequestParam(name="agentName", required=false) String agentName) {

		log.info("[CopyrightMessageController] 保存消息, sessionId: {}, role: {}", sessionId, role);

		try {
			CopyrightMessage message = copyrightMessageService.saveMessage(
					sessionId, role, content, messageType, agentName);
			return Result.OK("消息保存成功", message);
		} catch (Exception e) {
			log.error("[CopyrightMessageController] 消息保存失败", e);
			return Result.error("消息保存失败: " + e.getMessage());
		}
	}

	/**
	 * 获取会话的消息历史(分页)
	 *
	 * @param sessionId 会话ID
	 * @param pageNo    页码
	 * @param pageSize  每页大小
	 * @return 分页结果
	 */
	@Operation(summary="获取会话消息历史")
	@GetMapping(value = "/history/{sessionId}")
	public Result<IPage<CopyrightMessage>> getSessionMessages(
			@PathVariable("sessionId") String sessionId,
			@RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
			@RequestParam(name="pageSize", defaultValue="20") Integer pageSize) {

		log.info("[CopyrightMessageController] 查询会话消息, sessionId: {}, page: {}/{}", sessionId, pageNo, pageSize);

		Page<CopyrightMessage> page = new Page<>(pageNo, pageSize);
		IPage<CopyrightMessage> result = copyrightMessageService.getSessionMessages(sessionId, page);

		return Result.OK(result);
	}

	/**
	 * 获取会话的所有消息(不分页)
	 *
	 * @param sessionId 会话ID
	 * @return 消息列表
	 */
	@Operation(summary="获取会话所有消息")
	@GetMapping(value = "/all/{sessionId}")
	public Result<List<CopyrightMessage>> getAllSessionMessages(@PathVariable("sessionId") String sessionId) {
		log.info("[CopyrightMessageController] 查询会话所有消息, sessionId: {}", sessionId);

		List<CopyrightMessage> messages = copyrightMessageService.getSessionMessages(sessionId);
		return Result.OK(messages);
	}

	/**
	 * 获取会话的最近N条消息
	 *
	 * @param sessionId 会话ID
	 * @param limit     数量限制
	 * @return 消息列表
	 */
	@Operation(summary="获取最近N条消息")
	@GetMapping(value = "/recent/{sessionId}")
	public Result<List<CopyrightMessage>> getRecentMessages(
			@PathVariable("sessionId") String sessionId,
			@RequestParam(name="limit", defaultValue="10") Integer limit) {

		log.info("[CopyrightMessageController] 查询最近消息, sessionId: {}, limit: {}", sessionId, limit);

		List<CopyrightMessage> messages = copyrightMessageService.getRecentMessages(sessionId, limit);
		return Result.OK(messages);
	}

	/**
	 * 构建对话上下文
	 *
	 * @param sessionId 会话ID
	 * @param limit     包含的历史消息数量
	 * @return 对话上下文字符串
	 */
	@Operation(summary="构建对话上下文")
	@GetMapping(value = "/context/{sessionId}")
	public Result<String> buildDialogueContext(
			@PathVariable("sessionId") String sessionId,
			@RequestParam(name="limit", defaultValue="10") Integer limit) {

		log.info("[CopyrightMessageController] 构建对话上下文, sessionId: {}, limit: {}", sessionId, limit);

		String context = copyrightMessageService.buildDialogueContext(sessionId, limit);
		return Result.OK(context);
	}

	/**
	 * 删除会话的所有消息
	 *
	 * @param sessionId 会话ID
	 * @return 删除的消息数量
	 */
	@AutoLog(value = "软著申请消息-删除会话消息")
	@Operation(summary="删除会话的所有消息")
	@DeleteMapping(value = "/session/{sessionId}")
	public Result<String> deleteSessionMessages(@PathVariable("sessionId") String sessionId) {
		log.info("[CopyrightMessageController] 删除会话消息, sessionId: {}", sessionId);

		try {
			int count = copyrightMessageService.deleteSessionMessages(sessionId);
			return Result.OK("成功删除 " + count + " 条消息");
		} catch (Exception e) {
			log.error("[CopyrightMessageController] 删除会话消息失败", e);
			return Result.error("删除失败: " + e.getMessage());
		}
	}

	// ============= JeecgBoot标准CRUD接口 =============

	/**
	 * 分页列表查询
	 *
	 * @param copyrightMessage
	 * @param pageNo
	 * @param pageSize
	 * @param req
	 * @return
	 */
	//@AutoLog(value = "软著申请聊天记录-分页列表查询")
	@Operation(summary="软著申请聊天记录-分页列表查询")
	@GetMapping(value = "/list")
	public Result<IPage<CopyrightMessage>> queryPageList(CopyrightMessage copyrightMessage,
								   @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
								   @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
								   HttpServletRequest req) {


        QueryWrapper<CopyrightMessage> queryWrapper = QueryGenerator.initQueryWrapper(copyrightMessage, req.getParameterMap());
		Page<CopyrightMessage> page = new Page<CopyrightMessage>(pageNo, pageSize);
		IPage<CopyrightMessage> pageList = copyrightMessageService.page(page, queryWrapper);
		return Result.OK(pageList);
	}
	
	/**
	 *   添加
	 *
	 * @param copyrightMessage
	 * @return
	 */
	@AutoLog(value = "软著申请聊天记录-添加")
	@Operation(summary="软著申请聊天记录-添加")
	@RequiresPermissions("apply:copyright_apply_copyrightmessage:add")
	@PostMapping(value = "/add")
	public Result<String> add(@RequestBody CopyrightMessage copyrightMessage) {
		copyrightMessageService.save(copyrightMessage);

		return Result.OK("添加成功！");
	}
	
	/**
	 *  编辑
	 *
	 * @param copyrightMessage
	 * @return
	 */
	@AutoLog(value = "软著申请聊天记录-编辑")
	@Operation(summary="软著申请聊天记录-编辑")
	@RequiresPermissions("apply:copyright_apply_copyrightmessage:edit")
	@RequestMapping(value = "/edit", method = {RequestMethod.PUT,RequestMethod.POST})
	public Result<String> edit(@RequestBody CopyrightMessage copyrightMessage) {
		copyrightMessageService.updateById(copyrightMessage);
		return Result.OK("编辑成功!");
	}
	
	/**
	 *   通过id删除
	 *
	 * @param id
	 * @return
	 */
	@AutoLog(value = "软著申请聊天记录-通过id删除")
	@Operation(summary="软著申请聊天记录-通过id删除")
	@RequiresPermissions("apply:copyright_apply_copyrightmessage:delete")
	@DeleteMapping(value = "/delete")
	public Result<String> delete(@RequestParam(name="id",required=true) String id) {
		copyrightMessageService.removeById(id);
		return Result.OK("删除成功!");
	}
	
	/**
	 *  批量删除
	 *
	 * @param ids
	 * @return
	 */
	@AutoLog(value = "软著申请聊天记录-批量删除")
	@Operation(summary="软著申请聊天记录-批量删除")
	@RequiresPermissions("apply:copyright_apply_copyrightmessage:deleteBatch")
	@DeleteMapping(value = "/deleteBatch")
	public Result<String> deleteBatch(@RequestParam(name="ids",required=true) String ids) {
		this.copyrightMessageService.removeByIds(Arrays.asList(ids.split(",")));
		return Result.OK("批量删除成功!");
	}
	
	/**
	 * 通过id查询
	 *
	 * @param id
	 * @return
	 */
	//@AutoLog(value = "软著申请聊天记录-通过id查询")
	@Operation(summary="软著申请聊天记录-通过id查询")
	@GetMapping(value = "/queryById")
	public Result<CopyrightMessage> queryById(@RequestParam(name="id",required=true) String id) {
		CopyrightMessage copyrightMessage = copyrightMessageService.getById(id);
		if(copyrightMessage==null) {
			return Result.error("未找到对应数据");
		}
		return Result.OK(copyrightMessage);
	}

    /**
    * 导出excel
    *
    * @param request
    * @param copyrightMessage
    */
    @RequiresPermissions("apply:copyright_apply_copyrightmessage:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, CopyrightMessage copyrightMessage) {
        return super.exportXls(request, copyrightMessage, CopyrightMessage.class, "软著申请聊天记录");
    }

    /**
      * 通过excel导入数据
    *
    * @param request
    * @param response
    * @return
    */
    @RequiresPermissions("apply:copyright_apply_copyrightmessage:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        return super.importExcel(request, response, CopyrightMessage.class);
    }

}
