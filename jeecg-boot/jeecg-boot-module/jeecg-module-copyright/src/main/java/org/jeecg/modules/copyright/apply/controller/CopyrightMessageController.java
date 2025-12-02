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
 * @Description: 软著申请聊天记录
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Tag(name="软著申请聊天记录")
@RestController
@RequestMapping("/apply/copyrightMessage")
@Slf4j
public class CopyrightMessageController extends JeecgController<CopyrightMessage, ICopyrightMessageService> {
	@Autowired
	private ICopyrightMessageService copyrightMessageService;
	
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
