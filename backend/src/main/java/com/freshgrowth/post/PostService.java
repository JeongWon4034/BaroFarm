package com.freshgrowth.post;

import com.freshgrowth.common.AppException;
import com.freshgrowth.common.PageResponse;
import com.freshgrowth.post.dto.PostRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class PostService {
    private final PostMapper postMapper;

    public PostService(PostMapper postMapper) {
        this.postMapper = postMapper;
    }

    private static final java.util.Set<String> VALID_CATEGORIES =
            java.util.Set.of("general", "recipe", "tip", "question", "review");

    @Transactional
    public Post create(Long authorId, PostRequest request) {
        Post post = new Post();
        post.setAuthorId(authorId);
        post.setCategory(validCategory(request.getCategory()));
        post.setTitle(request.getTitle());
        post.setContent(request.getContent());
        postMapper.insert(post);
        return postMapper.findById(post.getPostId());
    }

    public PageResponse<Post> findAll(int page, int size, String keyword, String sort, String category) {
        int safePage = Math.max(page, 0);
        int safeSize = Math.min(Math.max(size, 1), 100);
        int offset = safePage * safeSize;
        String cat = (category != null && VALID_CATEGORIES.contains(category)) ? category : null;
        List<Post> content = postMapper.findAll(offset, safeSize, keyword, sort, cat);
        long total = postMapper.countAll(keyword, cat);
        return new PageResponse<>(content, safePage, safeSize, total);
    }

    @Transactional
    public Post findById(Long postId) {
        Post post = postMapper.findById(postId);
        if (post == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "POST_NOT_FOUND", "게시글을 찾을 수 없습니다.");
        }
        postMapper.increaseView(postId);
        post.setViewCount((post.getViewCount() == null ? 0 : post.getViewCount()) + 1);
        return post;
    }

    @Transactional
    public Post update(Long authorId, Long postId, PostRequest request) {
        if (postMapper.findById(postId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "POST_NOT_FOUND", "게시글을 찾을 수 없습니다.");
        }
        Post post = new Post();
        post.setPostId(postId);
        post.setAuthorId(authorId);
        post.setCategory(validCategory(request.getCategory()));
        post.setTitle(request.getTitle());
        post.setContent(request.getContent());
        if (postMapper.update(post) == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "수정 권한이 없습니다.");
        }
        return postMapper.findById(postId);
    }

    private String validCategory(String category) {
        return (category != null && VALID_CATEGORIES.contains(category)) ? category : "general";
    }

    @Transactional
    public void delete(Long authorId, Long postId) {
        if (postMapper.findById(postId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "POST_NOT_FOUND", "게시글을 찾을 수 없습니다.");
        }
        if (postMapper.delete(postId, authorId) == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "삭제 권한이 없습니다.");
        }
    }
}
