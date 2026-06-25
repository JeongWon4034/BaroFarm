package com.freshgrowth.upload;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.AppException;
import com.freshgrowth.common.auth.LoginRequired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * 상품 이미지 업로드 — 판매자가 자신의 사진을 등록. 서버 디렉터리에 저장하고 공개 URL(/uploads/xxx)을 돌려준다.
 * 저장 위치는 app.upload-dir(도커는 볼륨)이며, WebConfig가 /uploads/** 로 정적 서빙한다.
 */
@RestController
@RequestMapping("/api/v1")
public class UploadController {
    private static final Set<String> ALLOWED = Set.of("jpg", "jpeg", "png", "webp", "gif");

    private final Path uploadDir;

    public UploadController(@Value("${app.upload-dir:uploads}") String uploadDir) {
        this.uploadDir = Paths.get(uploadDir).toAbsolutePath();
    }

    @LoginRequired(role = "SELLER")
    @PostMapping(value = "/uploads", consumes = "multipart/form-data")
    public ApiResponse<?> upload(@RequestParam("file") MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new AppException(HttpStatus.BAD_REQUEST, "EMPTY_FILE", "이미지 파일을 선택해주세요.");
        }
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new AppException(HttpStatus.BAD_REQUEST, "NOT_IMAGE", "이미지 파일만 업로드할 수 있습니다.");
        }
        String ext = extensionOf(file.getOriginalFilename());
        if (!ALLOWED.contains(ext)) {
            throw new AppException(HttpStatus.BAD_REQUEST, "BAD_EXTENSION",
                    "jpg·png·webp·gif 형식만 업로드할 수 있습니다.");
        }

        String filename = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        try {
            Files.createDirectories(uploadDir);
            file.transferTo(uploadDir.resolve(filename));
        } catch (IOException e) {
            throw new AppException(HttpStatus.INTERNAL_SERVER_ERROR, "UPLOAD_FAILED", "이미지 저장에 실패했습니다.");
        }
        // 상대 경로 URL — Vite/nginx가 /uploads 를 백엔드로 프록시하므로 환경에 독립적
        return ApiResponse.ok("이미지를 업로드했습니다.", Map.of("url", "/uploads/" + filename));
    }

    private static String extensionOf(String name) {
        if (name == null) {
            return "";
        }
        int dot = name.lastIndexOf('.');
        return dot < 0 ? "" : name.substring(dot + 1).toLowerCase();
    }
}
