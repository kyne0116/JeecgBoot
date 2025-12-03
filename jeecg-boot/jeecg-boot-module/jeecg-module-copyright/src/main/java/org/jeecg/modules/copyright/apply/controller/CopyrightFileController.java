package org.jeecg.modules.copyright.apply.controller;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.io.*;
import java.net.URLDecoder;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.system.query.QueryGenerator;
import org.jeecg.common.system.query.QueryRuleEnum;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import org.jeecg.modules.copyright.apply.service.ICopyrightFileService;
import org.jeecg.modules.copyright.apply.service.FileDownloadService;
import org.jeecg.modules.copyright.apply.service.FileZipService;

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
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.multipart.MultipartHttpServletRequest;
import org.springframework.web.servlet.ModelAndView;
import com.alibaba.fastjson.JSON;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import org.jeecg.common.aspect.annotation.AutoLog;
import org.apache.shiro.authz.annotation.RequiresPermissions;
 /**
 * @Description: 软著文件记录
 * @Author: jeecg-boot
 * @Author: Claude Code (T007扩展)
 * @Date:   2025-12-02
 * @Version: V1.1
 */
@Tag(name="软著文件记录")
@RestController
@RequestMapping("/apply/copyrightFile")
@Slf4j
public class CopyrightFileController extends JeecgController<CopyrightFile, ICopyrightFileService> {
	@Autowired
	private ICopyrightFileService copyrightFileService;

	@Autowired
	private FileDownloadService downloadService;

	@Autowired
	private FileZipService zipService;
	
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

	// ==================== T007扩展接口 ====================

	/**
	 * 查询会话文件列表（T007）
	 *
	 * @param sessionId 会话ID
	 * @return 文件列表
	 */
	@Operation(summary = "查询会话文件列表", description = "查询指定会话的所有文件记录")
	@GetMapping(value = "/session/{sessionId}")
	public Result<List<CopyrightFile>> getSessionFiles(
			@Parameter(description = "会话ID", required = true)
			@PathVariable("sessionId") String sessionId) {

		log.info("[CopyrightFileController] 查询会话文件列表, sessionId: {}", sessionId);

		try {
			List<CopyrightFile> files = copyrightFileService.getSessionFiles(sessionId);
			log.info("[CopyrightFileController] 查询成功, 文件数量: {}", files.size());
			return Result.OK(files);

		} catch (Exception e) {
			log.error("[CopyrightFileController] 查询文件列表失败", e);
			return Result.error("查询文件列表失败: " + e.getMessage());
		}
	}

	/**
	 * 下载单个文件（T007）
	 *
	 * @param fileId 文件ID
	 * @return 文件流
	 */
	@Operation(summary = "下载单个文件", description = "根据文件ID下载文件")
	@GetMapping(value = "/download/{fileId}")
	public ResponseEntity<Resource> downloadFile(
			@Parameter(description = "文件ID", required = true)
			@PathVariable("fileId") String fileId) {

		log.info("[CopyrightFileController] 下载文件, fileId: {}", fileId);

		try {
			// 1. 查询文件记录
			CopyrightFile fileRecord = copyrightFileService.getById(fileId);
			if (fileRecord == null) {
				log.warn("[CopyrightFileController] 文件记录不存在, fileId: {}", fileId);
				return ResponseEntity.notFound().build();
			}

			// 2. 下载文件
			ResponseEntity<Resource> response = downloadService.downloadFile(fileRecord);
			log.info("[CopyrightFileController] 文件下载成功, fileId: {}", fileId);
			return response;

		} catch (FileNotFoundException e) {
			log.error("[CopyrightFileController] 文件不存在", e);
			return ResponseEntity.notFound().build();

		} catch (Exception e) {
			log.error("[CopyrightFileController] 文件下载失败", e);
			return ResponseEntity.internalServerError().build();
		}
	}

	/**
	 * 批量打包下载会话所有文件（T007）
	 *
	 * @param sessionId 会话ID
	 * @return ZIP文件流
	 */
	@Operation(summary = "批量打包下载", description = "将会话的所有文件打包为ZIP下载")
	@GetMapping(value = "/download-all/{sessionId}")
	public ResponseEntity<Resource> downloadAll(
			@Parameter(description = "会话ID", required = true)
			@PathVariable("sessionId") String sessionId) {

		log.info("[CopyrightFileController] 批量下载会话文件, sessionId: {}", sessionId);

		String zipFilePath = null;

		try {
			// 1. 查询会话所有文件
			List<CopyrightFile> files = copyrightFileService.getSessionFiles(sessionId);
			if (files.isEmpty()) {
				log.warn("[CopyrightFileController] 会话没有文件, sessionId: {}", sessionId);
				return ResponseEntity.noContent().build();
			}

			log.info("[CopyrightFileController] 准备打包 {} 个文件", files.size());

			// 2. 打包文件为ZIP
			zipFilePath = zipService.packSessionFiles(sessionId, files);

			// 3. 创建文件输入流
			File zipFile = new File(zipFilePath);
			if (!zipFile.exists()) {
				log.error("[CopyrightFileController] ZIP文件创建失败");
				return ResponseEntity.internalServerError().build();
			}

			FileInputStream inputStream = new FileInputStream(zipFile);
			InputStreamResource resource = new InputStreamResource(inputStream);

			// 4. 构建响应头
			String zipFilename = "copyright_" + sessionId + ".zip";
			HttpHeaders headers = new HttpHeaders();
			headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + zipFilename + "\"");
			headers.add(HttpHeaders.CONTENT_TYPE, "application/zip");
			headers.add(HttpHeaders.CONTENT_LENGTH, String.valueOf(zipFile.length()));

			log.info("[CopyrightFileController] ZIP打包下载成功, size: {} bytes", zipFile.length());

			// 5. 异步清理临时文件
			final String finalZipPath = zipFilePath;
			new Thread(() -> {
				try {
					Thread.sleep(10000); // 等待10秒后清理
					zipService.cleanupTempZip(finalZipPath);
				} catch (InterruptedException e) {
					Thread.currentThread().interrupt();
				}
			}).start();

			return ResponseEntity.ok()
					.headers(headers)
					.contentLength(zipFile.length())
					.contentType(MediaType.APPLICATION_OCTET_STREAM)
					.body(resource);

		} catch (Exception e) {
			log.error("[CopyrightFileController] 批量下载失败", e);

			// 清理失败的临时文件
			if (zipFilePath != null) {
				zipService.cleanupTempZip(zipFilePath);
			}

			return ResponseEntity.internalServerError().build();
		}
	}

}
