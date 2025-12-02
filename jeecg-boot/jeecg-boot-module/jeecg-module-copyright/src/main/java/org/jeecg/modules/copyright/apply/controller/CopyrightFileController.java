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
import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import org.jeecg.modules.copyright.apply.service.ICopyrightFileService;

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
 * @Description: 软著文件记录
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
@Tag(name="软著文件记录")
@RestController
@RequestMapping("/apply/copyrightFile")
@Slf4j
public class CopyrightFileController extends JeecgController<CopyrightFile, ICopyrightFileService> {
	@Autowired
	private ICopyrightFileService copyrightFileService;
	
	/**
	 * 分页列表查询
	 *
	 * @param copyrightFile
	 * @param pageNo
	 * @param pageSize
	 * @param req
	 * @return
	 */
	//@AutoLog(value = "软著文件记录-分页列表查询")
	@Operation(summary="软著文件记录-分页列表查询")
	@GetMapping(value = "/list")
	public Result<IPage<CopyrightFile>> queryPageList(CopyrightFile copyrightFile,
								   @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
								   @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
								   HttpServletRequest req) {


        QueryWrapper<CopyrightFile> queryWrapper = QueryGenerator.initQueryWrapper(copyrightFile, req.getParameterMap());
		Page<CopyrightFile> page = new Page<CopyrightFile>(pageNo, pageSize);
		IPage<CopyrightFile> pageList = copyrightFileService.page(page, queryWrapper);
		return Result.OK(pageList);
	}
	
	/**
	 *   添加
	 *
	 * @param copyrightFile
	 * @return
	 */
	@AutoLog(value = "软著文件记录-添加")
	@Operation(summary="软著文件记录-添加")
	@RequiresPermissions("apply:copyright_apply_copyrightfile:add")
	@PostMapping(value = "/add")
	public Result<String> add(@RequestBody CopyrightFile copyrightFile) {
		copyrightFileService.save(copyrightFile);

		return Result.OK("添加成功！");
	}
	
	/**
	 *  编辑
	 *
	 * @param copyrightFile
	 * @return
	 */
	@AutoLog(value = "软著文件记录-编辑")
	@Operation(summary="软著文件记录-编辑")
	@RequiresPermissions("apply:copyright_apply_copyrightfile:edit")
	@RequestMapping(value = "/edit", method = {RequestMethod.PUT,RequestMethod.POST})
	public Result<String> edit(@RequestBody CopyrightFile copyrightFile) {
		copyrightFileService.updateById(copyrightFile);
		return Result.OK("编辑成功!");
	}
	
	/**
	 *   通过id删除
	 *
	 * @param id
	 * @return
	 */
	@AutoLog(value = "软著文件记录-通过id删除")
	@Operation(summary="软著文件记录-通过id删除")
	@RequiresPermissions("apply:copyright_apply_copyrightfile:delete")
	@DeleteMapping(value = "/delete")
	public Result<String> delete(@RequestParam(name="id",required=true) String id) {
		copyrightFileService.removeById(id);
		return Result.OK("删除成功!");
	}
	
	/**
	 *  批量删除
	 *
	 * @param ids
	 * @return
	 */
	@AutoLog(value = "软著文件记录-批量删除")
	@Operation(summary="软著文件记录-批量删除")
	@RequiresPermissions("apply:copyright_apply_copyrightfile:deleteBatch")
	@DeleteMapping(value = "/deleteBatch")
	public Result<String> deleteBatch(@RequestParam(name="ids",required=true) String ids) {
		this.copyrightFileService.removeByIds(Arrays.asList(ids.split(",")));
		return Result.OK("批量删除成功!");
	}
	
	/**
	 * 通过id查询
	 *
	 * @param id
	 * @return
	 */
	//@AutoLog(value = "软著文件记录-通过id查询")
	@Operation(summary="软著文件记录-通过id查询")
	@GetMapping(value = "/queryById")
	public Result<CopyrightFile> queryById(@RequestParam(name="id",required=true) String id) {
		CopyrightFile copyrightFile = copyrightFileService.getById(id);
		if(copyrightFile==null) {
			return Result.error("未找到对应数据");
		}
		return Result.OK(copyrightFile);
	}

    /**
    * 导出excel
    *
    * @param request
    * @param copyrightFile
    */
    @RequiresPermissions("apply:copyright_apply_copyrightfile:exportXls")
    @RequestMapping(value = "/exportXls")
    public ModelAndView exportXls(HttpServletRequest request, CopyrightFile copyrightFile) {
        return super.exportXls(request, copyrightFile, CopyrightFile.class, "软著文件记录");
    }

    /**
      * 通过excel导入数据
    *
    * @param request
    * @param response
    * @return
    */
    @RequiresPermissions("apply:copyright_apply_copyrightfile:importExcel")
    @RequestMapping(value = "/importExcel", method = RequestMethod.POST)
    public Result<?> importExcel(HttpServletRequest request, HttpServletResponse response) {
        return super.importExcel(request, response, CopyrightFile.class);
    }

}
